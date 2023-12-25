import os
import cv2
import sys
import json
import time
import yaml
import logging
from PIL import Image

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from src.OCR.detection.text_detector import TextDetector
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.layout_analysis.layout_analyzer import LayoutAnalyzer
from utils.utility import padding_box, get_text_image, draw_boxes, preprocess_image, draw_layout_result, find_class_of_box, find_relative_position

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]

logging.getLogger().setLevel(logging.ERROR)
os.environ['CURL_CA_BUNDLE'] = ''

class InfoExtracter():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if InfoExtracter.__instance__ == None:
            InfoExtracter()
        return InfoExtracter.__instance__
    
    def __init__(self):
        if InfoExtracter.__instance__ != None:
            raise Exception("Prescription Parser is a singleton!")
        else:
            InfoExtracter.__instance__ == self
            self.detector = TextDetector.getInstance()
            self.recognizer = TextRecognizer.getInstance()
            self.layout_analyzer = LayoutAnalyzer.getInstance()
            self.text_extractor = TextExtractor.getInstance()


    def extract_info(self, image, is_visualize=False):
        """
        Match template with input image
        Input: input image
        Output: result image, result json file
        """
        start_time = time.time()
        status_code = "200"
        
        # preprocess image (~8s)
        image = preprocess_image(image)

        # document layout analysis
        layout_result = self.layout_analyzer.predict(image)

        # detect all boxes in image
        detection = self.detector.detect(image)
        detection.reverse()
        
        # recognize all texts
        recognition = []
        for box in detection:
            # box = padding_box(image, box, left_side = 0.001, right_side = 0.005, top_side = 0.06, bottom_side = 0.1)
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = self.recognizer.recognize(cropped_image)
            recognition.append(rec_result)


        with open('config/raw_template_form/don_xin_bao_luu_diem.json', 'r') as file:
            template = json.load(file)
        template_image = cv2.imread('data_form/don_xin_bao_luu_1.png')


        self.text_extractor.reset_info()
        print(time.time() - start_time)

        return result, status_code, []


if __name__ == "__main__":

    img_path = "src/data/written_file/don_mien_thi_1.jpg"
    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    paper_ocr = InfoExtracter()
    paper_ocr.extract_info(image)
