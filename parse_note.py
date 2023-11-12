import re
import subprocess
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image
from pytesseract import Output

TESSERACT_PATH = r"/opt/homebrew/bin/tesseract"

def find_notation_start(text):
    start_pattern = re.compile("\d{1,}[,\.]")
    matched_start = start_pattern.search(text)

    if matched_start is None:
        return None
    else:
        return matched_start.start()


def check_move_valid(move):
    """
    https://8bitclassroom.com/2020/08/16/chess-in-regex/
    """

    # regex for valid algebraic moves
    move_pattern = re.compile(
        "([Oo0](-[Oo0]){1,2}|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](\=[QRBN])?[+#]?(\s(1-0|0-1|1\/2-1\/2))?)"
    )

    if move_pattern.match(move) is None:
        return False
    else:
        return True


def clean_move(move):
    return move.replace(",", "")

def alternative_preprocessing(image):
    # take the cv2 image
    image = imutils.resize(image, width=700)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thresh = cv2.GaussianBlur(thresh, (3,3), 0)
    return thresh

def alternative_preprocessing_cropping_detection(image):
    imgr = cv2.imread("test2.png")
    # Resizing, converting...
    factor=3
    imgr = cv2.resize(imgr, (int(imgr.shape[1]*factor ), int(imgr.shape[0]*factor)), interpolation=cv2.INTER_AREA)

    # First detection in order to crop the image
    # We want a detection. Not important if result is bad.

    custom_config = r'--psm 6 -c tessedit_char_whitelist=.P123456RxB!tK-Ql'
    strings=pytesseract.image_to_data(imgr, lang = 'eng', config=custom_config)
    strings=strings.split('\n')
    for line in strings[2:]:
        s=line.split('\t')
        if len(s[11])>0:
            xmin=int(s[6])
            break


    ##  We crop the image to keep the interesting part...
    imgr=imgr[:,np.max([0,xmin-imgr.shape[1]//10]):,:]
    cv2.imshow("Cropped image",imgr)
    hsv = cv2.cvtColor(imgr, cv2.COLOR_BGR2HSV)
    h0, s0, Im0 = cv2.split(hsv)
    w=Im0.shape[1]  # From now, this is the image we will work on.
    h=Im0.shape[0]

    # Blob image to compute the image distortion
    blob=cv2.blur(Im0,(w//3,1))

    blob=cv2.normalize(blob,None,0,255,cv2.NORM_MINMAX)
    blob=cv2.threshold(blob,170,255,cv2.THRESH_BINARY)[1]
    cv2.imshow("Blob image",blob)

    x=[]
    y=[]
    for i in range(w):
        for j in range(h):
            if blob[j,i]==0:
                x.append(i)
                y.append(j)
    x=np.array(x)
    y=np.array(y)


    model = np.polyfit(x,y, 2)
    print("Regression parameters for the second-degree polynomial: ")
    print(model)

    plt.plot(x,y,'x')
    X=np.linspace(0,w)
    plt.plot(X,X*X*model[0]+X*model[1]+model[2])
    Ymean=np.mean(X*X*model[0]+X*model[1]+model[2])

    # Remapping the cropped image with the found model parameters


    map_x = np.zeros((Im0.shape[0], Im0.shape[1]), dtype=np.float32)
    map_y = np.zeros((Im0.shape[0], Im0.shape[1]), dtype=np.float32)
    for i in range(w):
        for j in range(h):
            map_x[j,i]=i
            map_y[j,i]=j+i*i*model[0]+i*model[1]+model[2]-Ymean


    Im1=cv2.remap(Im0, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    # Actual detection on the rectified image: Im1

    Im1=cv2.normalize(Im1,None,0,255,cv2.NORM_MINMAX)
    blur_radius=8
    threshold=120
    Im1= cv2.blur(Im1, (blur_radius,blur_radius))
    kernel = np.ones((4,4), np.uint8)
    Im1=255-cv2.erode(255-Im1, kernel)#, cv2.BORDER_REPLICATE)
    Im1=cv2.normalize(Im1,None,0,255,cv2.NORM_MINMAX)
    Im1 = cv2.threshold(Im1, threshold, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("Rectified image for text detection",Im1)

    strings=pytesseract.image_to_string(Im1, lang = 'eng', config=custom_config)

    strings=strings.split()
    strings=max(strings,key=len)
    print('=============================')
    print("Rectified image")
    print('RESULT: ',strings)
    print('=============================')


def ocr_text(png_file_input):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    # Load the image
    img = cv2.imread(str(png_file_input))

    # Convert to grayscale
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Get binary-mask
    # lwr = np.array([0, 0, 0])
    # upr = np.array([179, 255, 180])
    # msk = cv2.inRange(hsv, lwr, upr)

    # Up-sample
    # msk = cv2.resize(msk, (0, 0), fx=2, fy=2)

    # OCR
    return pytesseract.image_to_string(
        img, config="-c tessedit_char_blacklist=i%"
    ).replace("\n", "")


def extract_errors(file_name):
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


class Turn:
    def __init__(self, moves, sus):
        self.moves = moves
        self.sus = sus

    def __str__(self):
        return f"{self.moves} suspicious: {self.sus}"

    def __repr__(self):
        return str(self)


class Move:
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return str(self)


def move_delimiters(turn_count):
    # return [" " + str(turn_count) + ".", " " + str(turn_count) + ",.", " " + str(turn_count), str(turn_count) + ".", str(turn_count) + ",.", str(turn_count)]
    return [str(turn_count) + ".", str(turn_count) + ",."]


def get_inital_turn_count(note):
    # first, detect the inital turn count
    if note[:1] == "1.":
        return 1
    else:
        first_turn_index = note.find(".")
        return int(note[:first_turn_index])


def check_suspicious(turn_text, invalid_move_text):
    # check if the move text appears to be suspicous (exclude move number for now)
    for invalid_text in invalid_move_text:
        # print(f"mv: {invalid_text} {note[:next_index + len(min_delimiter)]}")
        if invalid_text in turn_text.lower():
            print("Suspicious!")
            return True
    return False


def parse_move_text(invalid_move_text, note):
    notation_start = find_notation_start(note)

    # print(f"not start {notation_start}")
    # print(note)

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
            print("No next index")
            final_turn = True
            next_index = len(note)
            min_delimiter = ""
        else:
            min_delimiter = min(matched_next_indices, key=matched_next_indices.get)
            next_index = matched_next_indices[min_delimiter]

        if note[:next_index].strip() != "":
            is_suspicious = check_suspicious(note[:next_index], invalid_move_text)
            # print(f"raw turn text is {note[:next_index].strip().split(' ')}")
            raw_turn_text = note[:next_index].strip().split(" ")
            raw_turn_text = filter(lambda x: x.strip() != "", raw_turn_text)
            # if its the final turn, filter moves which don't appear legit and only take first two moves
            if final_turn:
                raw_turn_text = list(filter(check_move_valid, raw_turn_text))[:2]

            move_to_add = []
            for mv in raw_turn_text:
                mv = clean_move(mv)
                move_to_add.append(Move(mv))

            turns.append(Turn(move_to_add, is_suspicious))
        turn_count += 1
        note = note[next_index + len(min_delimiter) :]

        if final_turn:
            break

    return turns


if __name__ == "__main__":
    # Set the directory path
    dir_path = Path(__file__).parent / Path("my_system_notation_samples")

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
        pgn_file_name = f"intermediate/{png_input.name.replace('png', 'pgn')}"
        note = ocr_text(png_input)

        # write the parsed pgn to a file
        with open(pgn_file_name, "w") as f:
            f.write(note)

        invalid_move_text = extract_errors(pgn_file_name)
        turns = parse_move_text(invalid_move_text, note)
        print(turns)
