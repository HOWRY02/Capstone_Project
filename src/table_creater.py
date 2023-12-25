import os
import cv2
import sys
import time
import yaml
import logging
from PIL import Image

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from src.OCR.detection.text_detector import TextDetector
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.form_understanding.form_understand import FormUnderstand
from utils.utility import get_text_image, draw_layout_result, make_underscore_name

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]

logging.getLogger().setLevel(logging.ERROR)
os.environ['CURL_CA_BUNDLE'] = ''

class TemplateCreater():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if TemplateCreater.__instance__ == None:
            TemplateCreater()
        return TemplateCreater.__instance__
    
    def __init__(self):
        if TemplateCreater.__instance__ != None:
            raise Exception("Prescription Parser is a singleton!")
        else:
            TemplateCreater.__instance__ == self
            self.detector = TextDetector.getInstance()
            self.recognizer = TextRecognizer.getInstance()
            self.form_understand = FormUnderstand.getInstance()
            self.text_extractor = TextExtractor.getInstance()

    def create_table(self, image, is_visualize=False):
        """
        Match template with input image
        Input: input image
        Output: result image, result json file
        """
        start_time = time.time()
        status_code = "200"

        template = {'title':    {'box':[], 'text':[]},
                    'question': {'box':[], 'text':[]},
                    'date':     {'box':[], 'text':[]}}

        # form understanding
        form_result = self.form_understand.predict(image)

        # find template boxes
        title_boxes = form_result['title']['box'].copy()
        question_boxes = form_result['question']['box'].copy()

        # find template title
        title_texts = []
        for box in title_boxes:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = self.recognizer.recognize(cropped_image)
            title_texts.append(rec_result)

        template['title']['box'] = title_boxes
        template['title']['text'] = title_texts

        form_name, position_of_form_name = self.text_extractor.extract_form_name(template['title'])

        template['title']['box'] = [position_of_form_name]
        template['title']['text'] = make_underscore_name([form_name])

        # find template question
        question_texts = []
        for box in question_boxes:
            cropped_image = get_text_image(image, box)
            rec_result = self.find_text_in_big_box(cropped_image)
            question_texts.append(rec_result)
        
        question_texts = self.text_extractor.extract_column_name(question_texts)

        template['question']['box'] = question_boxes
        template['question']['text'] = make_underscore_name(question_texts)

        # find template date
        if len(form_result['date']['box']) > 0:
            template['date']['box'].append(form_result['date']['box'][0])
            template['date']['text'].append('ngay_tao_don')

        template_json = []
        for key_template, value_template in template.items():
            for i, box in enumerate(value_template['box']):
                element = {'box': box,
                           'text': value_template['text'][i],
                           'class': key_template}
                template_json.append(element)

        form_img = None
        if is_visualize:
            form_img = draw_layout_result(image, form_result, box_width=2, box_alpha=0.1)

        self.text_extractor.reset_info()
        print(time.time() - start_time)

        return template_json, status_code, [image, form_img]


    def find_text_in_big_box(self, image):
        # detect all boxes in image
        detection = self.detector.detect(image)
        detection.reverse()
        
        # recognize all texts
        recognition = []
        for box in detection:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = self.recognizer.recognize(cropped_image)
            recognition.append(rec_result)

        text = ' '.join(recognition)

        return text


if __name__ == "__main__":

    img_path = "config/template/don_mien_thi.png"
    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    template_creater = TemplateCreater()
    template = template_creater.create_table(image)
