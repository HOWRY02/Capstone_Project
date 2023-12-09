import os
import cv2
import sys
import json
import unidecode
from PIL import Image

from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.form_understanding.form_understand import FormUnderstand
from src.DBMS.db_manager import DBManager
from utils.utility import get_text_image

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

class TableCreater():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if TableCreater.__instance__ == None:
            TableCreater()
        return TableCreater.__instance__
    
    def __init__(self):
        if TableCreater.__instance__ != None:
            raise Exception("Prescription Parser is a singleton!")
        else:
            TableCreater.__instance__ == self

            self.recognizer = TextRecognizer.getInstance()
            self.form_understand = FormUnderstand.getInstance()
            self.db_manager = DBManager.getInstance()
            self.text_extractor = TextExtractor.getInstance()


    def create_template(self, image, form_result, ):
        """
        Match template with input image
        Input: input image
        Output: result image, result json file
        """
        template = {'title':     {'box':[], 'text':[]},
                    'question':  {'box':[], 'text':[]}}

        # form understanding
        # form_result = self.form_understand.predict(image)

        question_boxes = form_result['question']['box']

        # title_texts = []
        # for box in title_boxes:
        #     cropped_image = get_text_image(image, box)
        #     cropped_image = Image.fromarray(cropped_image)
        #     rec_result = self.recognizer.recognize(cropped_image)
        #     title_texts.append(rec_result)

        question_texts = []
        for box in question_boxes:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = self.recognizer.recognize(cropped_image)
            question_texts.append(rec_result)


        form_name, position_of_form_name = self.text_extractor.extract_form_name(form_result['title'])

        template['title']['box'] = position_of_form_name
        template['title']['text'] = form_name

        template['question']['box'] = question_boxes
        template['question']['text'] = self.make_column_name(question_texts)

        template['question']['box'].append(form_result['date']['box'])
        template['question']['text'].append('ngay_tao_don')

        # json_object = json.dumps(template, indent=4)

        return template


    def make_column_name(self, question_texts):
        
        for i, text in enumerate(question_texts):
            lower_text = text.lower()
            ascii_text = unidecode.unidecode(lower_text)
            ascii_words_in_text = ascii_text.split()

            question_texts[i] = ' '.join(ascii_words_in_text)

        return question_texts

if __name__ == "__main__":

    img_path = "src/data_form/don_mien_thi.png"
    image = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    paper_ocr = TableCreater()
    template = paper_ocr.create_template(image)
    print(template)
