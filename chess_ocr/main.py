import argparse
from pathlib import Path

from chess_ocr.core import Notation


def parser_handler(input_directory: str) -> None:
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
        print("\n \n ------------------------")

        n = Notation(file_path)
        print("Raw turns: ", n.turns)
        print("Suspicious turns: ", n.get_suspicious_turns())
        print("Turn suggestions: ", n.get_turn_suggestions())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_directory",
        type=str,
        help="The relative path to the directory containing your notation samples to be parsed.",
    )
    args = parser.parse_args()
    parser_handler(args.input_directory)
