import os
import sys
from ultralytics import YOLO
from utils.utility import find_relative_position

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

class FormUnderstand():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if FormUnderstand.__instance__ == None:
            FormUnderstand()
        return FormUnderstand.__instance__

    def __init__(self):
        if FormUnderstand.__instance__ != None:
            raise Exception('Text Recognizer is a singleton!')
        else:
            FormUnderstand.__instance__ = self
            self.model = YOLO('model/doc_model/yolov8_instance_segmentation/document_understanding/v1/best.pt')


    def format_form_result(self, form_result):
        index_of_class = {0:'answer', 1:'date', 2:'question', 3:'title'}

        classes = form_result[0].boxes.cls.cpu().numpy().astype(int).tolist()
        boxes = form_result[0].boxes.xyxy.cpu().numpy().astype(int).tolist()
        confidence = form_result[0].boxes.conf.cpu().numpy()

        new_form_result = {'answer':      {'box':[], 'confidence':[]},
                           'date':        {'box':[], 'confidence':[]},
                           'question':    {'box':[], 'confidence':[]},
                           'title':       {'box':[], 'confidence':[]}}

        for i, val in enumerate(classes):
            new_form_result[index_of_class[val]]['box'].append(boxes[i])
            new_form_result[index_of_class[val]]['confidence'].append(confidence[i])

        return new_form_result
    

    def predict(self, image, conf=0.4):
        
        new_image = image.copy()
        form_result = self.format_form_result(self.model.predict(new_image, conf=conf, verbose=False))

        for key_form, value_form in form_result.items():
            value_form['box'].sort(key = lambda x: x[1])

            for i, box in enumerate(value_form['box']):
                relative_position = find_relative_position(value_form['box'][i-1], box)
                if relative_position == 1:
                    value_form['box'][i][1] = min(value_form['box'][i-1][1], box[1])
                    value_form['box'][i-1][1] = min(value_form['box'][i-1][1], box[1])

            value_form['box'].sort(key = lambda x: (x[1], x[0]))

        return form_result
