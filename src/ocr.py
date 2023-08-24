import cv2
import os
import sys
import time
import logging
from PIL import Image
from OCR.detection.detector import TextDetector
from OCR.recognition.recognizer import TextRecognizer

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

logging.getLogger().setLevel(logging.ERROR)
os.environ['CURL_CA_BUNDLE'] = ''


class OCR():
    def __init__(self) -> None:
        self.text_detector = TextDetector()
        self.text_recognizer = TextRecognizer()


    def extractInfo(self, img_path):

        image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        
        det_boxes = self.text_detector.detector(img_path)
        # print(det_boxes)

        for box in det_boxes:
            cropped_image = image[box[0][1]:box[2][1], box[0][0]:box[1][0]]
            rec_result = self.text_recognizer.recognizer(cropped_image)
            text = rec_result
            print(text)


if __name__ == "__main__":
    start_time = time.time()
    img_path = "data/prescription.png"
    ocr = OCR()
    ocr.extractInfo(img_path)

    print(time.time() - start_time)

