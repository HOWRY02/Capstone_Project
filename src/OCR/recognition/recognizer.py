import os
import sys
from PIL import Image
from OCR.paddleocr import PaddleOCR

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'


class TextRecognizer():
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def recognizer(self, img):
        rec_result = self.ocr.ocr(img, cls=False, det=False, rec=True)

        text, time_pr = rec_result[0][0]

        return text

