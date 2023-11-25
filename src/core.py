import argparse
import copy
import re
import subprocess
from pathlib import Path

import cv2
import pytesseract

from openai_api import (build_combined_move_suggestion_prompt, chat_completion,
                        test_next_move_prediction, test_valid_algebraic)
from preprocessing import clean_move
from representations import Move, Turn

FIRST_NOTATION_TURN = "\d{1,}[,\.]"
VALID_ALGEBRAIC_MOVE = "([Oo0](-[Oo0]){1,2}|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](\=[QRBN])?[+#]?(\s(1-0|0-1|1\/2-1\/2))?)"

INTERMEDIATE_FILE_LOCATION = "/Users/james/Documents/code/chess_ocr/intermediate"

# tesseract setup
TESSERACT_PATH = r"/opt/homebrew/bin/tesseract"
TESSERACT_CONFIG = "-c tessedit_char_blacklist=i%"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def build_PGN(turns: list[Turn], **kwargs) -> str:
    PERMITTED_PGN_HEADERS = [
        "Event",
        "Site",
        "Date",
        "Round",
        "White",
        "Black",
        "Result",
    ]

    # build result iteratively
    PGN_result = ""

    for key, value in kwargs.items():
        if key not in PERMITTED_PGN_HEADERS:
            raise Exception("PGN key not in allowed list.")

        PGN_result += f'[{key} "{value}"]\n'

    PGN_result += "\n"

    for turn in turns:
        PGN_result += str(turn.number) + ". "
        for move in turn.moves:
            PGN_result += move.move_text + " "

    return PGN_result


def find_notation_start(text: str) -> int:
    start_pattern = re.compile(FIRST_NOTATION_TURN)
    matched_start = start_pattern.search(text)

    if matched_start is None:
        return -1
    else:
        return matched_start.start()


def check_move_valid(move: str) -> bool:
    """
    https://8bitclassroom.com/2020/08/16/chess-in-regex/
    """

    # regex for valid algebraic moves
    move_pattern = re.compile(VALID_ALGEBRAIC_MOVE)
    if move_pattern.match(move) is None:
        return False
    else:
        return True


def ocr_text(png_file_input: Path) -> str:
    # Load the image
    img = cv2.imread(str(png_file_input))
    # img = preprocessing_gray_binary_upsample(img)

    return pytesseract.image_to_string(img, config=TESSERACT_CONFIG).replace("\n", "")


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


def move_delimiters(turn_count: int) -> list[str]:
    # return [" " + str(turn_count) + ".", " " + str(turn_count) + ",.", " " + str(turn_count), str(turn_count) + ".", str(turn_count) + ",.", str(turn_count)]
    return [str(turn_count) + ".", str(turn_count) + ",."]


def get_inital_turn_count(note: str) -> int:
    # first, detect the inital turn count
    if note[:1] == "1.":
        return 1
    else:
        first_turn_index = note.find(".")
        return int(note[:first_turn_index])


def split_joined_moves(joined_move_text: str):
    # search for two valid moves
    for char_counter in range(1, len(joined_move_text)):
        if check_move_valid(joined_move_text[:char_counter]) and check_move_valid(
            joined_move_text[char_counter:]
        ):
            return [joined_move_text[:char_counter], joined_move_text[char_counter:]]

    # search for one valid move
    for char_counter in range(1, len(joined_move_text)):
        if check_move_valid(joined_move_text[:char_counter]) or check_move_valid(
            joined_move_text[char_counter:]
        ):
            return [joined_move_text[:char_counter], joined_move_text[char_counter:]]

    return None


def check_turn_suspicious(turn_text: str, invalid_move_text: list[str]) -> bool:
    # check if the move text appears to be suspicous (exclude move number for now)
    for invalid_text in invalid_move_text:
        # print(f"mv: {invalid_text} {note[:next_index + len(min_delimiter)]}")
        if invalid_text in turn_text.lower():
            return True
    return False


def parse_move_text(inital_note: str) -> tuple[list[Turn], int, int]:
    note = inital_note
    notation_start = find_notation_start(note)

    note = note[notation_start:]
    next_turn_count = get_inital_turn_count(note)
    turns = []
    final_turn = False

    while True:
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
            # print(f"raw turn text is {note[:next_index].strip().split(' ')}")
            raw_turn_text = note[:next_index].strip().split(" ")
            raw_turn_text = list(filter(lambda x: x.strip() != "", raw_turn_text))
            # if its the final turn, filter moves which don't appear legit and only take first two moves
            if final_turn:
                # print(f"final turn raw_turn_text is {raw_turn_text}")
                raw_turn_text = list(filter(check_move_valid, raw_turn_text))[:2]
                # there is a bug here if the last turn notation appears multiple time in the string?
                notation_end = inital_note.find(raw_turn_text[-1]) + len(
                    raw_turn_text[-1]
                )

            # split move text of turn which is missing a space between moves
            if (
                len(raw_turn_text) == 1
                and (split_move := split_joined_moves(raw_turn_text[0])) != None
            ):
                print("triggered split!")
                raw_turn_text = split_move

            moves_to_add = [Move(clean_move(mv)) for mv in raw_turn_text]
            turns.append(
                Turn(
                    moves_to_add,
                    next_turn_count - 1,
                    True if len(moves_to_add) != 2 and not final_turn else False,
                )
            )

        next_turn_count += 1
        note = note[next_index + len(min_delimiter) :]

        if final_turn:
            break

    return turns, notation_start, notation_end


def parse_suspicions(turns: list[Turn], invalid_move_text: list[str]):
    for t in turns:
        t.sus = t.sus or check_turn_suspicious(str(t), invalid_move_text)

    return turns


def parser_handler(input_directory: str) -> None:
    # Set the directory path
    dir_path = Path(input_directory)

    # List all files recursively
    all_files = [
        file
        for file in dir_path.rglob("*")
        if file.is_file() and ".DS" not in file.name and "ex12" in file.name
    ]

    for file_path in sorted(all_files):
        print("\n \n ------------------------")
        print(f"This file is {file_path}")
        print("\n \n ------------------------")

        png_input = file_path
        pgn_file_name = (
            f"{INTERMEDIATE_FILE_LOCATION}/{png_input.name.replace('png', 'pgn')}"
        )
        note = ocr_text(png_input)

        turns, notation_start, notation_end = parse_move_text(note)

        # write the parsed pgn to a file
        with open(pgn_file_name, "w") as f:
            f.write(note[notation_start:notation_end])

        invalid_move_text = extract_errors(pgn_file_name)

        turns = parse_suspicions(turns, invalid_move_text)
        print(turns)

        edited_turns = copy.copy(turns)

        for turn in edited_turns:
            for move in turn.moves:
                if not check_move_valid(move.move_text):
                    print("Recommended new move")
                    move.move_text = test_valid_algebraic(move.move_text)[
                        "move_text_suggestion"
                    ]

        print(edited_turns)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_directory",
        type=str,
        help="The relative path to the directory containing your notation samples to be parsed.",
    )
    args = parser.parse_args()
    parser_handler(args.input_directory)
