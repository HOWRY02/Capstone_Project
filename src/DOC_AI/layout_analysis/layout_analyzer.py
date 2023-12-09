import os
import sys
from ultralytics import YOLO

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

class LayoutAnalyzer():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if LayoutAnalyzer.__instance__ == None:
            LayoutAnalyzer()
        return LayoutAnalyzer.__instance__

    def __init__(self):
        if LayoutAnalyzer.__instance__ != None:
            raise Exception('Text Recognizer is a singleton!')
        else:
            LayoutAnalyzer.__instance__ = self
            self.model = YOLO('model/doc_model/yolov8_instance_segmentation/document_layout_analysis/best.pt')


    def format_layout_result(self, layout_result):
        index_of_class = {0:'figure', 1:'list', 2:'table', 3:'text', 4:'title'}

        classes = layout_result[0].boxes.cls.cpu().numpy().astype(int).tolist()
        boxes = layout_result[0].boxes.xyxy.cpu().numpy().astype(int).tolist()
        confidence = layout_result[0].boxes.conf.cpu().numpy()

        new_layout_result = {'list':    {'box':[], 'confidence':[]}, 
                             'table':   {'box':[], 'confidence':[]}, 
                             'title':   {'box':[], 'confidence':[]}, 
                             'figure':  {'box':[], 'confidence':[]}, 
                             'text':    {'box':[], 'confidence':[]}}

        for i, val in enumerate(classes):
            new_layout_result[index_of_class[val]]['box'].append(boxes[i])
            new_layout_result[index_of_class[val]]['confidence'].append(confidence[i])
            
        return new_layout_result
    

    def predict(self, image, conf=0.4):
        
        new_image = image.copy()
        layout_result = self.format_layout_result(self.model.predict(new_image, conf=conf))

        return layout_result
