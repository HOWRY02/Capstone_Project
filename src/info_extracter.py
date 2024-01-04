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
from utils.utility import make_underscore_name, get_text_image, preprocess_image, align_images, find_class_of_box, draw_layout_result, find_relative_position

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
        Output: template image, template json file
        """
        start_time = time.time()
        status_code = "200"
        
        # preprocess image (~8s)
        image = preprocess_image(image)

        title = {'box':[], 'text':[]}

        # document layout analysis
        layout_document = self.layout_analyzer.predict(image)

        # find template boxes
        title_boxes = layout_document['title']['box'].copy()

        # find template title
        title_texts = []
        for box in title_boxes:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_template = self.recognizer.recognize(cropped_image)
            title_texts.append(rec_template)

        title['box'] = title_boxes
        title['text'] = title_texts
        print(title_texts)
        form_name, position_of_form_name = self.text_extractor.extract_form_name(title)
        form_name = make_underscore_name([form_name])[0]

        with open(f"config/template_form/{form_name}.json", 'r') as file:
            template = json.load(file)
        template_image = cv2.imread(f"config/template/{form_name}.jpg")

        aligned = align_images(image, template_image, debug=False)

        layout_template = self.layout_analyzer.predict(aligned)

        for loc in template:
            [x_t, y_t, x_b, y_b] = loc['box']
            roi = aligned[y_t:y_b, x_t:x_b]
            cropped_image = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            ocr_text = self.find_text_in_big_box(cropped_image)
            loc['ocr_text'] = ocr_text

        table_question = []
        table_answer = []
        for i, loc in enumerate(template):
            class_of_box = find_class_of_box(loc['box'], layout_template)
            if class_of_box == 'table':
                if loc['class'] == 'question':
                    table_question.append(loc['text'])
                else:
                    loc['text'] = table_question[len(table_answer)] if len(table_question) != 0 else ''
                    table_answer.append(loc['text'])
            else:
                if loc['class'] == 'answer':
                    loc['text'] = template[i-1]['text']
        
        result = []
        for i, loc in enumerate(template):
            if loc['class'] != 'question':
                result.append(loc)

        if is_visualize:
            layout_img = draw_layout_result(image, layout_document, box_width=2, box_alpha=0.1)
            cv2.imwrite('result/layout_img.jpg', layout_img)

        self.text_extractor.reset_info()
        print(time.time() - start_time)

        return result, status_code, [aligned]


    def find_text_in_big_box(self, image):
        # detect all boxes in image
        detection = self.detector.detect(image)
        if detection is not None:
            detection.sort(key = lambda x: x[0][1])
            for i, box in enumerate(detection):
                relative_position = find_relative_position(detection[i-1], box)
                if relative_position == 1:
                    detection[i][0][1] = min(detection[i-1][0][1], box[0][1])
                    detection[i-1][0][1] = min(detection[i-1][0][1], box[0][1])
            detection.sort(key = lambda x: (x[0][1], x[0][0]))

            # recognize all texts
            recognition = []
            for box in detection:
                cropped_image = get_text_image(image, box)
                cropped_image = Image.fromarray(cropped_image)
                rec_template = self.recognizer.recognize(cropped_image)
                recognition.append(rec_template)

            text = ' '.join(recognition)
        else:
            text = ''

        return text


if __name__ == "__main__":

    img_path = "data/printed_file/don_mien_thi_1.png"
    image = cv2.imread(img_path, cv2.IMREAD_COLOR)
    info_extracter = InfoExtracter()
    template, status_code, [aligned] = info_extracter.extract_info(image, is_visualize=True)
