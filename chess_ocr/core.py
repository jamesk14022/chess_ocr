import copy
import subprocess
import urllib.parse
from pathlib import Path

import cv2
import pytesseract

from chess_ocr.openai_api import test_valid_algebraic
from chess_ocr.parsing import (
    check_move_valid,
    find_notation_start,
    get_inital_turn_count,
    move_delimiters,
    split_joined_moves,
)
from chess_ocr.preprocessing import clean_move

FIRST_NOTATION_TURN = "\d{1,}[,\.]"
VALID_ALGEBRAIC_MOVE = "([Oo0](-[Oo0]){1,2}|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](\=[QRBN])?[+#]?(\s(1-0|0-1|1\/2-1\/2))?)"

INTERMEDIATE_FILE_LOCATION = "/Users/james/Documents/code/chess_ocr/intermediate"

# tesseract setup
TESSERACT_PATH = r"/opt/homebrew/bin/tesseract"
TESSERACT_CONFIG = "-c tessedit_char_blacklist=i%"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class Move:
    def __init__(self, move_text: str):
        self.move_text = move_text

    def __str__(self) -> str:
        return self.move_text

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict:
        return {"move_text": self.move_text}


class Turn:
    def __init__(self, moves: list[Move], number: int, sus: bool = False):
        self.number: int = number
        self.moves: list[Move] = moves
        self.sus: bool = sus

    def __str__(self) -> str:
        return f"{self.number}: {self.moves} suspicious: {self.sus}"

    def __repr__(self) -> str:
        return str(self)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "moves": [m.to_dict() for m in self.moves],
            "sus": self.sus,
        }


class Notation:
    def __init__(self, image_loc: Path) -> None:
        self.image_loc = image_loc
        self.image = cv2.imread(str(self.image_loc))
        self.turns, self.notation_end = Notation.parse_move_text(self.text)

    def __len__(self):
        return len(self.turns)

    @property
    def text(self) -> str:
        raw_text = pytesseract.image_to_string(
            self.image, config=TESSERACT_CONFIG
        ).replace("\n", "")
        self.notation_start = find_notation_start(raw_text)
        return raw_text[self.notation_start :]

    @property
    def analysis_url(self) -> str:
        encoded_pgn = urllib.parse.quote(self.build_PGN().strip())
        return f"https://lichess.org/analysis/pgn/{encoded_pgn}"

    @staticmethod
    def parse_move_text(inital_note: str) -> tuple[list[Turn], int]:
        note = inital_note

        next_turn_count = get_inital_turn_count(note)
        turns = []
        final_turn = False

        while not final_turn:
            move_delimiter_next = move_delimiters(next_turn_count)
            matched_next_indices = {
                d: note.find(d) for d in move_delimiter_next if note.find(d) != -1
            }

            if len(matched_next_indices) == 0:
                final_turn = True
                next_index = len(note)
                min_delimiter = ""
            else:
                min_delimiter = min(
                    matched_next_indices, key=matched_next_indices.__getitem__
                )
                next_index = matched_next_indices[min_delimiter]

            if note[:next_index].strip() != "":
                raw_turn_text = note[:next_index].strip().split(" ")
                raw_turn_text = list(filter(lambda x: x.strip() != "", raw_turn_text))
                # if its the final turn, filter moves which don't appear legit and only take first two moves
                if final_turn:
                    raw_turn_text = list(filter(check_move_valid, raw_turn_text))[:2]
                    # there is a bug here if the last turn notation appears multiple time in the string?
                    notation_end = inital_note.find(raw_turn_text[-1]) + len(
                        raw_turn_text[-1]
                    )

                # split move text of turn which is missing a space between moves
                if (
                    len(raw_turn_text) == 1
                    and not check_move_valid(raw_turn_text[0])
                    and (split_move := split_joined_moves(raw_turn_text[0])) != None
                ):
                    raw_turn_text = split_move

                moves_to_add = [
                    Move(clean_move(mv)) for mv in raw_turn_text if clean_move(mv)
                ]
                turns.append(
                    Turn(
                        moves_to_add,
                        next_turn_count - 1,
                        True if len(moves_to_add) != 2 and not final_turn else False,
                    )
                )

            next_turn_count += 1
            note = note[next_index + len(min_delimiter) :]

        return turns, notation_end

    def get_suspicious_turns(self) -> list[Turn]:
        pgn_file_name = f"{INTERMEDIATE_FILE_LOCATION}/{str(self.image_loc).split('/')[-1].replace('png', 'pgn')}"
        with open(pgn_file_name, "w") as f:
            f.write(self.text[self.notation_start : self.notation_end])
        invalid_move_text = extract_errors(pgn_file_name)
        return parse_suspicions(self.turns, invalid_move_text)

    def build_PGN(self, **kwargs) -> str:
        PERMITTED_PGN_HEADERS = [
            "Event",
            "Site",
            "Date",
            "Round",
            "White",
            "Black",
            "Result",
        ]

        PGN_result = ""
        for key, value in kwargs.items():
            if key not in PERMITTED_PGN_HEADERS:
                raise Exception("PGN key not in allowed list.")

            PGN_result += f'[{key} "{value}"]\n'

        PGN_result += "\n"

        for turn in self.turns:
            PGN_result += str(turn.number) + "."
            for move in turn.moves:
                PGN_result += move.move_text + " "

        return PGN_result


def get_turn_suggestions(notation: Notation) -> list[Turn]:
    edited_notation = copy.copy(notation)
    for turn in edited_notation.turns:
        for move in turn.moves:
            if not check_move_valid(move.move_text):
                move.move_text = test_valid_algebraic(move.move_text)[
                    "move_text_suggestion"
                ]

    return edited_notation


def extract_errors(file_name: str) -> list[str]:
    out_lines = (
        subprocess.run(["./pgn-extract", "-r", file_name], capture_output=True)
        .stderr.decode("UTF-8")
        .split("\n")
    )

    invalid_move_text = []

    for line in out_lines:
        if "Unknown character" in line:
            print(f"unknown char: {line.split(' ')[2].strip()}")
            invalid_move_text.append(line.split(" ")[2].strip())
        if "Unknown move text" in line:
            print(f"unknown move text: {line.split(' ')[3].strip()}")
            invalid_move_text.append(line.split(" ")[3].strip())

    return invalid_move_text


def check_turn_suspicious(turn_text: str, invalid_move_text: list[str]) -> bool:
    # check if the move text appears to be suspicous (exclude move number for now)
    for invalid_text in invalid_move_text:
        if invalid_text in turn_text.lower():
            return True
    return False


def parse_suspicions(turns: list[Turn], invalid_move_text: list[str]):
    for t in turns:
        t.sus = t.sus or check_turn_suspicious(str(t), invalid_move_text)

    return turns
