import asyncio
from pathlib import Path
from PIL import Image
import pytesseract
from stardust.apps.myfreecams.handleurls import MfcNetActions
from stardust.apps.myfreecams.helper import calc_img_hash
from PIL import ImageEnhance
import cv2
import numpy as np

alo = [
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test00.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test01.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test02.jpg"),
    Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test03.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test04.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test05.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test06.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test07.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test08.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test09.jpg"),
    # Path("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/test10.jpg"),
]

# h = calc_img_hash(a)
# ha = calc_img_hash(b)
# print(h, ha)

# y= Image.open(a)
# z=Image.open(b)
# n= Image.open(c)
# m=Image.open(d)
# k=Image.open(a)

# Open the image
# custom_config = r"-c tessedit_char_blacklist=)., --oem 3 --psm 6"
# for x in alo:
#     image = Image.open(x)
    # Enhance the image for better OCR results
    # enhancer = ImageEnhance.Brightness(image)
    # ei = enhancer.enhance(0.4)
    # ei = ImageEnhance.Contrast(image)
    # er = ei.enhance(0.4)
    # ec = er.convert("L")
    # rr = pytesseract.image_to_string(image, lang="eng", config=custom_config).split()
    # rr = pytesseract.image_to_string(ei, lang="eng", config="--psm 6").strip()

    # if "MyFreeCams" in rr:
    #     print("Cams",x.stem)
    #     continue
    # if "MyFreeGams" in rr:
    #     print("Gams",x.stem)
    #     continue

    # print()
    # print(x.stem)
    # print(rr)
    # set1 = set(rr)
    # set2 = ["MyFreeCams", "MyFreeGams", "currently", "webcam"]
    # common_items = [item for item in set2 if item in rr]
    # print(rr)
    # print(x.stem, common_items)


# img = cv2.imread("/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/b.jpg")

# Adding custom options

# op = pytesseract.image_to_string(img, config=custom_config).split()
# print()
# print(op)

# img = cv2.imread('/mnt/Alpha/_bey/uv/helio/stardust/apps/myfreecams/assets/hash/b.jpg')

def preprocess(img_path):
    img = cv2.imread(img_path, 0)

    # Rescale if needed
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Contrast stretching
    a = 0.2
    b = 0.9 
    c = 255 / (b - a)
    d = -a * c
    img = cv2.add(cv2.multiply(img, c), d)

    # Gaussian blur 
    img = cv2.GaussianBlur(img, (5,5), 0)

    # Adaptive thresholding
    img_bin = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Noise removal
    kernel = np.ones((3,3),np.uint8)
    img_bin = cv2.erode(img_bin, kernel, iterations = 1)
    img_bin = cv2.dilate(img_bin, kernel, iterations = 1)

    # Skew correction
    coords = np.column_stack(np.where(img_bin > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle        
    (h, w) = img_bin.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    img_bin = cv2.warpAffine(img_bin, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return img_bin




# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# noise removal
def remove_noise(image):
    return cv2.medianBlur(image, 5)


# thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


# dilation
def dilate(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)


# erosion
def erode(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.erode(image, kernel, iterations=1)


# opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5, 5), np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)


# canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)


# skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated

def resize(image):
    return cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

def binary(img_gray):
    _, img_bin = cv2.threshold(img_gray, 0, 155, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return img_bin


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

config = r'-c tessedit_char_blacklist=), --oem 3 --psm 6'
for x in alo:
    image = cv2.imread(f"{x}")

    gray = get_grayscale(image)
    thresh = thresholding(gray)
    openin = opening(gray)
    cann = canny(gray)

    gray2=get_grayscale(image)
    rd=binary(gray2)
    # resized =resize(rd)
    resized=preprocess(x)


    fg = pytesseract.image_to_string(image, config=config).split()
    fx = pytesseract.image_to_string(thresh, config=config).split()
    fy = pytesseract.image_to_string(resized, config=config).split()

    set1 = set(fg)
    set2 = ["MyFreeCams", "MyFreeGams", "currently", "webcam", "from", "away"]
    common = [item for item in set2 if item in fg]

    set1 = set(fx)
    com = [item for item in set2 if item in fx]

    set1 = set(fy)
    cfy = [item for item in set2 if item in fy]
    # print(fg)
    print(x.stem, len(common), len(com),len(cfy))
    print(fy)
    # print()
