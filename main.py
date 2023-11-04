from PIL import Image
import pandas as pd
from pytesseract import Output
import cv2
import numpy as np

import pytesseract

# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# Load the image
img = cv2.imread("no_symbol_algebraic2.png")

# Convert to grayscale
#hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Get binary-mask
#lwr = np.array([0, 0, 0])
#upr = np.array([179, 255, 180])
#msk = cv2.inRange(hsv, lwr, upr)

# Up-sample
#msk = cv2.resize(msk, (0, 0), fx=2, fy=2)

# OCR
txt = pytesseract.image_to_string(img)
print(txt)


### Get a searchable PDF
#pdf = pytesseract.image_to_pdf_or_hocr('no_symbol_algebraic.png', extension='pdf')
#with open('test.pdf', 'w+b') as f:
#    f.write(pdf) # pdf type is bytes by default
#
#
#img = cv2.imread('no_symbol_algebraic.png')
#img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#kernel = np.ones((1, 1), np.uint8)
#img = cv2.dilate(img, kernel, iterations=1)
#img = cv2.erode(img, kernel, iterations=1)
##img = cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#
##img = cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#
##2img = cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#
#img = cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#
##img = cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#
##img = cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#
#img = cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#
#cv2.imwrite('preproc.png', img)
#
#custom_config = r'--psm 6 -c tessedit_char_whitelist=!.-RPQKNB012345678chxoO'
#d = pytesseract.image_to_data(img, config=custom_config, output_type=Output.DICT)
#df = pd.DataFrame(d)
#print(df)
#
#
#print(pytesseract.image_to_string(img, config=custom_config))
#
