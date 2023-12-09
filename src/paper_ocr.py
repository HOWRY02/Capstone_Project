import os
import cv2
import sys
import time
import yaml
import logging
from PIL import Image
from src.OCR.detection.text_detector import TextDetector
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.layout_analysis.layout_analyzer import LayoutAnalyzer
from src.DOC_AI.form_understanding.form_understand import FormUnderstand
from utils.utility import padding_box, get_text_image, draw_boxes, preprocess_image, draw_layout_result, find_class_of_box, find_relative_position

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]

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

            self.recognizer = TextRecognizer.getInstance()
            self.detector = TextDetector.getInstance()
            self.layout_analyzer = LayoutAnalyzer.getInstance()
            self.form_understand = FormUnderstand.getInstance()
            self.text_extractor = TextExtractor.getInstance()


    def extract_info(self, image, is_visualize):
        """
        Match template with input image
        Input: input image
        Output: result image, result json file
        """
        start_time = time.time()
        status_code = "200"
        with open('config/init_result.json') as yaml_file:
            result = yaml.safe_load(yaml_file)
        
        # preprocess image (~8s)
        # image = preprocess_image(image)

        # document layout analysis and form understanding
        layout_result = self.layout_analyzer.predict(image)
        form_result = self.form_understand.predict(image)

        # detect all boxes in image
        detection = self.detector.detect(image)
        detection.reverse()
        
        if detection is None:
            return result, '460'
        count = 0
        recognition = []
        for box in detection:
            # box = padding_box(image, box, left_side = 0.001, right_side = 0.005, top_side = 0.06, bottom_side = 0.1)
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            cropped_image.save(f"src/result/img/cropped_image_{count}.jpg")
            rec_result = self.recognizer.recognize(cropped_image)
            recognition.append(rec_result)
            count += 1
        
        new_layout_result = {'title':   {'box':[], 'text':[]},
                             'text':    {'box':[], 'text':[]},
                             'table':   {'box':[], 'text':[]},
                             'list':    {'box':[], 'text':[]},
                             'figure':  {'box':[], 'text':[]},
                             'other':   {'box':[], 'text':[]}}
        for i, box in enumerate(detection):
            class_of_box = find_class_of_box(box, layout_result)
            new_layout_result[class_of_box]['box'].append(box)
            new_layout_result[class_of_box]['text'].append(recognition[i])

        question_region = new_layout_result['title']['box'] + new_layout_result['text']['box'] \
            + new_layout_result['table']['box']
        question_region_text = new_layout_result['title']['text'] + new_layout_result['text']['text'] \
            + new_layout_result['table']['text']

        new_form_result = {'title':     {'box':[], 'text':[]},
                           'question':  {'box':[], 'text':[]},
                           'answer':    {'box':[], 'text':[]},
                           'date':      {'box':[], 'text':[]}}
        for key_form, value_form in form_result.items():
            for form_box in value_form['box']:
                text_list = []
                for i, box in enumerate(question_region):
                    relative_position = find_relative_position(form_box, box)
                    if relative_position == 0:
                        text_list.append(question_region_text[i])

                text = ' '.join(text_list)
                new_form_result[key_form]['box'].append(form_box)
                new_form_result[key_form]['text'].append(text)

        # print(new_form_result)

        form_name, position_of_form_name = self.text_extractor.extract_form_name(new_form_result['title'])

        result["form_name"] = form_name

        boxes_img = None
        layout_img = None
        form_img = None
        if is_visualize:
            boxes_img = draw_boxes(image, detection)
            layout_img = draw_layout_result(image, layout_result, box_width=2, box_alpha=0.1)
            form_img = draw_layout_result(image, form_result, box_width=2, box_alpha=0.1)

        self.text_extractor.reset_info()
        print(time.time() - start_time)

        return result, status_code, [boxes_img,layout_img,form_img]


if __name__ == "__main__":

    img_path = "src/data/written_file/don_mien_thi_1.jpg"
    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    paper_ocr = PaperOcrParser()
    paper_ocr.extract_info(image)
