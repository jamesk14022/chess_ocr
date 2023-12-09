import re

FIRST_NOTATION_TURN = "\d{1,}[,\.]"
VALID_ALGEBRAIC_MOVE = "([Oo0](-[Oo0]){1,2}|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](\=[QRBN])?[+#]?(\s(1-0|0-1|1\/2-1\/2))?)"


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
