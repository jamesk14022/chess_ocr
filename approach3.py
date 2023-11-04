import cv2
import pytesseract
import imutils

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

image = cv2.imread('test2.png')
image = imutils.resize(image, width=700)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
thresh = cv2.GaussianBlur(thresh, (3,3), 0)
data = pytesseract.image_to_string(thresh, lang='eng', config='--psm 6')
print(data)

cv2.imshow('thresh', thresh)
cv2.imwrite('thresh.png', thresh)
cv2.waitKey()
