import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
# Read image
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


# For comparison: detection on the non rectified image
# using the same parameters:


Im2 = Im0 #  whithout remapping
Im2 = cv2.normalize(Im2,None,0,255,cv2.NORM_MINMAX)
Im2 = cv2.blur(Im2, (blur_radius,blur_radius))
Im2 = 255-cv2.erode(255-Im2, kernel)#, cv2.BORDER_REPLICATE)
Im2 = cv2.normalize(Im2,None,0,255,cv2.NORM_MINMAX)
Im2 = cv2.threshold(Im2, threshold, 255, cv2.THRESH_BINARY)[1]

strings=pytesseract.image_to_string(Im2, lang = 'eng', config=custom_config)

strings=strings.split()
strings=max(strings,key=len)
print('================================================')
print("Test on the non rectified image")
print("with the same blur, erode, threshold and")
print("tesseract parameters")
print('RESULT: ',strings)
print('================================================')
cv2.imshow("Unrectified image for text detection",Im2)


# Close windows


print("Press any key on an opened opencv window to close")
cv2.waitKey()
plt.close()
cv2.destroyAllWindows()
