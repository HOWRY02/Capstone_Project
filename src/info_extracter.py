import os
import cv2
import sys
import json
import time
import yaml
import copy
from PIL import Image

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from src.OCR.detection.text_detector import TextDetector
from src.OCR.recognition.text_recognizer import TextRecognizer
from src.OCR.extraction.text_extractor import TextExtractor
from src.DOC_AI.layout_analysis.layout_analyzer import LayoutAnalyzer
from src.utils.utility import make_underscore_name, get_text_image, preprocess_image, align_images, find_class_of_box, draw_layout_result, find_relative_position, find_text_in_big_box

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]


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
            raise Exception("This class is a singleton!")
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
        print(image.shape)
        start_time = time.time()
        status_code = "200"
        
        # preprocess image (~8s)
        # image = preprocess_image(image)

        title = {'box':[], 'text':[]}

        # document layout analysis
        layout_document = self.layout_analyzer.predict(image)

        # find template boxes
        title['box'] = layout_document['title']['box'].copy()

        # find template title
        for box in title['box']:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_template = self.recognizer.recognize(cropped_image)
            title['text'].append(rec_template)

        print(title['text'])
        form_name, _ = self.text_extractor.extract_form_name(title)
        form_name = make_underscore_name([form_name])[0]

        with open(f"config/template_form/{form_name}.json", 'r') as file:
            template = json.load(file)
        template_image = cv2.imread(f"config/template/{form_name}.jpg")

        aligned = align_images(image, template_image, debug=False)

        detection = self.detector.detect(aligned)
        detection.reverse()

        for loc in template:
            for answer in loc['answer_text']:
                answer_box = []
                for box in detection:
                    temp_box = copy.deepcopy(box)
                    if box[0][0] < answer['box'][0] and box[1][0] > answer['box'][0]:
                        temp_box[0][0] = answer['box'][0]
                        temp_box[3][0] = answer['box'][0]
                    if box[0][0] < answer['box'][2] and box[1][0] > answer['box'][2]:
                        temp_box[1][0] = answer['box'][2]
                        temp_box[2][0] = answer['box'][2]
                    area_temp_box = (temp_box[1][0]-temp_box[0][0])*(temp_box[3][1]-temp_box[0][1])
                    area_box = (answer['box'][2]-answer['box'][0])*(answer['box'][3]-answer['box'][1])
                    if area_temp_box/area_box > 0.1:
                        relative_position = find_relative_position(answer['box'], temp_box)
                        if relative_position == 0:
                            answer_box.append(temp_box)

                answer['temp_box'] = answer_box

        result = []
        for loc in template:
            for answer in loc['answer_text']:
                for box in answer['temp_box']:
                    cropped_image = get_text_image(aligned, box)
                    cropped_image = Image.fromarray(cropped_image)
                    rec_result = self.recognizer.recognize(cropped_image)
                    answer['text'] += rec_result
                answer.pop('temp_box', None)

            result.append(loc)

        if is_visualize:
            layout_img = draw_layout_result(image, layout_document, box_width=2, box_alpha=0.1)
            cv2.imwrite('result/layout_img.jpg', layout_img)

        self.text_extractor.reset_info()
        print(time.time() - start_time)

        return result, status_code, [aligned]


if __name__ == "__main__":

    img_path = "data/written_file/400_DPI_resized/don_mien_thi_1.png"
    image = cv2.imread(img_path, cv2.IMREAD_COLOR)
    info_extracter = InfoExtracter()
    template, status_code, [aligned] = info_extracter.extract_info(image, is_visualize=True)
