import os
import sys
from PIL import Image
from OCR.paddleocr import PaddleOCR

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'


class TextDetector():
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def detector(self, img_path):
        result = self.ocr.ocr(img_path, cls=True, det=True, rec=False)

        dt_boxes = []
        for line in result[0]:
            dt_boxes.append([[int(line[0][0]), int(line[0][1])], 
                          [int(line[1][0]), int(line[1][1])], 
                          [int(line[2][0]), int(line[2][1])], 
                          [int(line[3][0]), int(line[3][1])]])

        return dt_boxes

