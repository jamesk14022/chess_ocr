import argparse
import re
import subprocess
from pathlib import Path

from preprocessing import clean_move
from representations import Move, Turn
import cv2
import pytesseract

FIRST_NOTATION_TURN = "\d{1,}[,\.]"
VALID_ALGEBRAIC_MOVE = "([Oo0](-[Oo0]){1,2}|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](\=[QRBN])?[+#]?(\s(1-0|0-1|1\/2-1\/2))?)"

INTERMEDIATE_FILE_LOCATION = "/Users/james/Documents/code/chess_ocr/intermediate"

# tesseract setup 
TESSERACT_PATH = r"/opt/homebrew/bin/tesseract"
TESSERACT_CONFIG = "-c tessedit_char_blacklist=i%"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

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

    return pytesseract.image_to_string(
        img, config=TESSERACT_CONFIG
    ).replace("\n", "")


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
    turn_count = get_inital_turn_count(note)
    turns = []
    final_turn = False

    while True:
        move_delimiter_next = move_delimiters(turn_count)
        matched_next_indices = {
            d: note.find(d) for d in move_delimiter_next if note.find(d) != -1
        }

        # print(matched_next_indices)
        # print(note)

        if len(matched_next_indices) == 0:
            final_turn = True
            next_index = len(note)
            min_delimiter = ""
        else:
            min_delimiter = min(matched_next_indices, key=matched_next_indices.__getitem__)
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
                notation_end = inital_note.find(raw_turn_text[-1]) + len(raw_turn_text[-1])

            moves_to_add = [Move(clean_move(mv)) for mv in raw_turn_text]
            turns.append(Turn(moves_to_add, True if len(moves_to_add)!=2 and not final_turn else False))

        turn_count += 1
        note = note[next_index + len(min_delimiter) :]

        if final_turn:
            break

    return turns, notation_start, notation_end 

def parse_suspicions(turns: list[Turn], invalid_move_text: list[str]):

    for t in turns:
        t.sus = t.sus or check_turn_suspicious(str(t), invalid_move_text)

    return turns

def parser_handler(input_directory: str) -> list[Turn]:
    # Set the directory path
    dir_path = Path(input_directory)

    # List all files recursively
    all_files = [
        file
        for file in dir_path.rglob("*")
        if file.is_file() and ".DS" not in file.name
    ]

    for file_path in sorted(all_files):
        print("\n \n ------------------------")
        print(f"This file is {file_path}")

        png_input = file_path
        pgn_file_name = f"{INTERMEDIATE_FILE_LOCATION}/{png_input.name.replace('png', 'pgn')}"
        note = ocr_text(png_input)

        print(f"raw ocr {note}")

        turns, notation_start, notation_end = parse_move_text(note)

        
        print(f"truncated ocr {note[notation_start:notation_end]}")

        # write the parsed pgn to a file
        with open(pgn_file_name, "w") as f:
            f.write(note[notation_start:notation_end])


        invalid_move_text = extract_errors(pgn_file_name)
        print(f"The invalid move text is {invalid_move_text}")
        print(parse_suspicions(turns, invalid_move_text))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_directory", type=str, help="The relative path to the directory containing your notation samples to be parsed.")
    args = parser.parse_args()
    parser_handler(args.input_directory)

    
