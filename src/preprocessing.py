import numpy as np
import pytesseract
import cv2
import imutils
from numpy import ndarray
import matplotlib.pyplot as plt

IMAGE_RESIZE_FACTOR=3

def clean_move(move_text: str) -> str:
    return move_text.replace(",", "").replace(".", "")

def preprocessing_gray_binary_upsample(image: ndarray) -> ndarray:

    # Convert to grayscale
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Get binary-mask
    lwr = np.array([0, 0, 0])
    upr = np.array([179, 255, 180])
    msk = cv2.inRange(hsv, lwr, upr)

    # Up-sample
    msk = cv2.resize(msk, (0, 0), fx=2, fy=2)
    return msk

def alternative_preprocessing(image: ndarray) -> ndarray:
    # take the cv2 image
    image = imutils.resize(image, width=700)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thresh = cv2.GaussianBlur(thresh, (3, 3), 0)
    return thresh


def alternative_preprocessing_cropping_detection(image: ndarray) -> ndarray:

    imgr = cv2.resize(
        image,
        (int(image.shape[1] * IMAGE_RESIZE_FACTOR), int(image.shape[0] * IMAGE_RESIZE_FACTOR)),
        interpolation=cv2.INTER_AREA,
    )

    # First detection in order to crop the image
    # We want a detection. Not important if result is bad.

    custom_config = r"--psm 6 -c tessedit_char_whitelist=.P123456RxB!tK-Ql"
    strings = pytesseract.image_to_data(imgr, lang="eng", config=custom_config)
    strings = strings.split("\n")
    for line in strings[2:]:
        s = line.split("\t")
        if len(s[11]) > 0:
            xmin = int(s[6])
            break

    ##  We crop the image to keep the interesting part...
    imgr = imgr[:, np.max([0, xmin - imgr.shape[1] // 10]) :, :]
    cv2.imshow("Cropped image", imgr)
    hsv = cv2.cvtColor(imgr, cv2.COLOR_BGR2HSV)
    h0, s0, Im0 = cv2.split(hsv)
    w = Im0.shape[1]  # From now, this is the image we will work on.
    h = Im0.shape[0]

    # Blob image to compute the image distortion
    blob = cv2.blur(Im0, (w // 3, 1))

    blob = cv2.normalize(blob, None, 0, 255, cv2.NORM_MINMAX)
    blob = cv2.threshold(blob, 170, 255, cv2.THRESH_BINARY)[1]
    cv2.imshow("Blob image", blob)

    x = []
    y = []
    for i in range(w):
        for j in range(h):
            if blob[j, i] == 0:
                x.append(i)
                y.append(j)
    x_arr = np.array(x)
    y_arr = np.array(y)

    model = np.polyfit(x_arr, y_arr, 2)
    print("Regression parameters for the second-degree polynomial: ")
    print(model)

    plt.plot(x_arr, y_arr, "x")
    X = np.linspace(0, w)
    plt.plot(X, X * X * model[0] + X * model[1] + model[2])
    Ymean = np.mean(X * X * model[0] + X * model[1] + model[2])

    # Remapping the cropped image with the found model parameters

    map_x = np.zeros((Im0.shape[0], Im0.shape[1]), dtype=np.float32)
    map_y = np.zeros((Im0.shape[0], Im0.shape[1]), dtype=np.float32)
    for i in range(w):
        for j in range(h):
            map_x[j, i] = i
            map_y[j, i] = j + i * i * model[0] + i * model[1] + model[2] - Ymean

    Im1 = cv2.remap(
        Im0,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )

    # Actual detection on the rectified image: Im1

    Im1 = cv2.normalize(Im1, None, 0, 255, cv2.NORM_MINMAX)
    blur_radius = 8
    threshold = 120
    Im1 = cv2.blur(Im1, (blur_radius, blur_radius))
    kernel = np.ones((4, 4), np.uint8)
    Im1 = 255 - cv2.erode(255 - Im1, kernel)  # , cv2.BORDER_REPLICATE)
    Im1 = cv2.normalize(Im1, None, 0, 255, cv2.NORM_MINMAX)
    Im1 = cv2.threshold(Im1, threshold, 255, cv2.THRESH_BINARY)[1]
    return Im1