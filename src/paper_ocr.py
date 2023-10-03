## here is implement REST API
import cv2
import sys
import time
import json
import yaml
import numpy as np
from src.OCR.detection.text_detector import TextDetector
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from utils.utility import *

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]

import os
import logging

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

logging.getLogger().setLevel(logging.ERROR)
os.environ['CURL_CA_BUNDLE'] = ''


class PaperOcrParser():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PaperOcrParser.__instance__ == None:
            PaperOcrParser()
        return PaperOcrParser.__instance__
    
    def __init__(self):
        if PaperOcrParser.__instance__ != None:
            raise Exception("Prescription Parser is a singleton!")
        else:
            PaperOcrParser.__instance__ == self
        self.lang = "en"
        self.recognizer = TextRecognizer(self.lang)
        self.detector = TextDetector.getInstance()
        self.text_extraction = TextExtractor(self.lang)


    def extract_info(self, image, is_visualize=True):
        """
        Match template with input image
        Input: input image
        Output: result image, result json file
        """
        start_time = time.time()
        status_code = "200"
        with open('src/result/init_result.json') as yaml_file:
            result = yaml.safe_load(yaml_file)
        
        # detect all boxes in image
        detection = self.detector.detect(image)
        detection.reverse()
        
        if detection is None:
            return result, '460'
        
        recognition = []
        for box in detection:
            # box = padding_box(image, box, left_side = 0.001, right_side = 0.005, top_side = 0.06, bottom_side = 0.1)
            cropped_image = get_text_image(image, box)
            rec_result = self.recognizer.recognize(cropped_image)
            recognition.append(rec_result)
            # print(rec_result)

        for i, text in enumerate(recognition):
            position_follow_up, is_form_name = self.text_extraction.extract_form_name(text, detection[i])
            if is_form_name:
                break

        result["form_name"] = self.text_extraction.classify_form_name()

        boxes_img = image.copy()
        if is_visualize:
            boxes_img = draw_boxes_ocr(boxes_img, detection)

        self.text_extraction.reset_info()
        print(time.time() - start_time)
        return result, status_code, boxes_img


    def change_language(self, lang):
        """Desc:
        en: English version
        vi: Vietnamese khong dau
        vi1: Vietnamese co dau
        """
        if self.lang != lang:
            self.lang = lang
            if lang == 'vi1':
                self.recognizer.change_language("vi")
                lang = 'vi'
            else:
                self.recognizer.change_language("en")


if __name__ == "__main__":
    start_time = time.time()
    img_path = "data/prescription.png"
    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    paper_ocr = PaperOcrParser()
    paper_ocr.extract_info(image)
    print(time.time() - start_time)
