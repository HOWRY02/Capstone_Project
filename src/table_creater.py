import os
import cv2
import sys
import time
import yaml

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from src.OCR.detection.text_detector import TextDetector
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.form_understanding.form_understand import FormUnderstand
from src.DOC_AI.layout_analysis.layout_analyzer import LayoutAnalyzer
from src.utils.utility import preprocess_image, get_text_image, draw_layout_result, make_underscore_name
from src.utils.utility import find_text_in_big_box, create_answer_boxes_in_table

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]


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
            raise Exception("This class is a singleton!")
        else:
            TableCreater.__instance__ == self
            self.detector = TextDetector.getInstance()
            self.recognizer = TextRecognizer.getInstance()
            self.form_understand = FormUnderstand.getInstance()
            self.layout_analyzer = LayoutAnalyzer.getInstance()
            self.text_extractor = TextExtractor.getInstance()

    def create_table(self, image, is_visualize=False):
        """
        Match template with input image
        Input: input image
        Output: result image, result json file
        """
        print(image.shape)
        start_time = time.time()
        status_code = "200"

        # preprocess image
        # image = preprocess_image(image)

        template = {'title':    {'box':[], 'text':[]},
                    'question': {'box':[], 'text':[]},
                    'answer':   {'box':[], 'text':[]},
                    'date':     {'box':[], 'text':[]},
                    'table':    {'box':[], 'text':[]}}

        # form understanding
        form_result = self.form_understand.predict(image)

        # document layout analysis
        layout_result = self.layout_analyzer.predict(image)

        # find template boxes
        for key in form_result:
            template[key]['box'] = form_result[key]['box']

        # find answer boxes and texts in table
        if len(layout_result['table']['box']) > 0:
            template['answer']['box'] = create_answer_boxes_in_table(image, layout_result['table']['box'][0])
            template['answer']['text'] = ['' for _ in template['answer']['box']]

        # find template texts
        for key in template:
            for box in template[key]['box']:
                cropped_image = get_text_image(image, box)
                rec_result = find_text_in_big_box(self.detector, self.recognizer, cropped_image)
                template[key]['text'].append(rec_result)
        
        form_name, position_of_form_name = self.text_extractor.extract_form_name(template['title'])
        question_texts = self.text_extractor.extract_column_name(template['question']['text'])

        template['title']['box'] = [position_of_form_name]
        template['title']['text'] = make_underscore_name([form_name])
        template['question']['text'] = make_underscore_name(question_texts)
        template['date']['text'] = ['ngay_tao_don' for _ in template['date']['box']]
        template['table']['box'] = layout_result['table']['box']
        template['table']['text'] = ['bang' for _ in template['table']['box']]

        template_json = []
        for key_template, value_template in template.items():
            for i, box in enumerate(value_template['box']):
                element = {'box': box,
                           'text': value_template['text'][i],
                           'class': key_template}
                template_json.append(element)

        if is_visualize:
            form_img = draw_layout_result(image, form_result, box_width=2, box_alpha=0.1)
            cv2.imwrite('result/form_img.jpg', form_img)

        self.text_extractor.reset_info()
        print(time.time() - start_time)

        return template_json, status_code, []


if __name__ == "__main__":

    img_path = "data/scanned_data_form/1200_DPI_PNG_RISIZED/don_xin_mien_thi.png"
    image = cv2.imread(img_path, cv2.IMREAD_COLOR)
    table_creater = TableCreater()
    template_json, status_code, [] = table_creater.create_table(image)
