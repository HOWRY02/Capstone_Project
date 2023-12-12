import os
import cv2
import sys
import time
import yaml
import logging
import unidecode
from PIL import Image
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.form_understanding.form_understand import FormUnderstand
from utils.utility import preprocess_image, get_text_image, remove_special_characters, draw_layout_result

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

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

            self.recognizer = TextRecognizer.getInstance()
            self.form_understand = FormUnderstand.getInstance()
            self.text_extractor = TextExtractor.getInstance()

    def create(self, image, is_visualize):
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

        # preprocess image (~8s)
        # image = preprocess_image(image)

        # form understanding
        form_result = self.form_understand.predict(image)

        title_boxes = form_result['title']['box'].copy()
        question_boxes = form_result['question']['box'].copy()

        title_texts = []
        for box in title_boxes:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = self.recognizer.recognize(cropped_image)
            title_texts.append(rec_result)

        template['title']['box'] = title_boxes
        template['title']['text'] = title_texts

        question_texts = []
        for box in question_boxes:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = self.recognizer.recognize(cropped_image)
            question_texts.append(rec_result)
        question_texts = self.text_extractor.extract_column_name(question_texts)

        form_name, position_of_form_name = self.text_extractor.extract_form_name(template['title'])

        template['title']['box'] = [position_of_form_name]
        template['title']['text'] = self.make_column_name([form_name])

        template['question']['box'] = question_boxes
        template['question']['text'] = self.make_column_name(question_texts)

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

        # print(template_json)

        form_img = None
        if is_visualize:
            form_img = draw_layout_result(image, form_result, box_width=2, box_alpha=0.1)

        self.text_extractor.reset_info()
        print(time.time() - start_time)
        return template_json, status_code, [image, form_img]


    def make_column_name(self, text_list):

        for i, text in enumerate(text_list):
            lower_text = text.lower()
            ascii_text = unidecode.unidecode(lower_text)
            ascii_text = remove_special_characters(ascii_text)
            ascii_words_in_text = ascii_text.split()

            while '' in ascii_words_in_text:
                ascii_words_in_text.remove('')

            text_list[i] = '_'.join(ascii_words_in_text)

        return text_list


if __name__ == "__main__":

    img_path = "src/data_form/don_mien_thi.png"
    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    template_creater = TemplateCreater()
    template = template_creater.create(image)
