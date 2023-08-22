import cv2
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.append("/home/intern-hvphuc2/prescription-ocr/src/utils")

from OCR.paddleocr import PaddleOCR

import logging

logging.getLogger().setLevel(logging.ERROR)
os.environ['CURL_CA_BUNDLE'] = ''

# need to run only once to download and load model into memory
ocr = PaddleOCR(use_angle_cls=True, lang='en')

img_path = 'data/prescription.png'

img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

result = ocr.ocr(img_path, cls=True, det=True, rec=False)

boxes = []
for line in result[0]:
    boxes.append([[int(line[0][0]), int(line[0][1])],
                    [int(line[2][0]), int(line[2][1])]])

# print(boxes)
for box in boxes:
    cropped_image = img[box[0][1]:box[1][1], box[0][0]:box[1][0]]
    rec_result = ocr.ocr(cropped_image, cls=False, det=False, rec=True)
    text = rec_result[0]
    print(text)

