import os
import sys
from argparse import Namespace

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

from src.OCR.detection.text_detection import TextDetection

def sort_index(lst, rev=True):
    index = range(len(lst))
    s = sorted(index, reverse=rev, key=lambda i: lst[i])
    return s

class TextDetector(TextDetection):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextDetector.__instance__ == None:
            TextDetector()
        return TextDetector.__instance__

    def __init__(self):
        if TextDetector.__instance__ != None:
            raise Exception('Paddle Text Recognizer is a singleton!')
        else:
            TextDetector.__instance__ = self

            self.rec_args = Namespace(
                det_algorithm="DB",
                use_gpu=True,
                use_npu=False,
                use_xpu=False,
                gpu_mem=500,
                det_limit_side_len=960,
                det_limit_type="max",
                det_db_thresh=0.3,
                det_db_box_thresh=0.5,
                det_db_unclip_ratio=1.5,
                max_batch_size=10,
                use_dilation=False,
                det_db_score_mode="fast",
                det_model_dir="model/detection_model",
                det_box_type="quad",
                use_onnx=False,
                use_tensorrt=False,
                benchmark=False,
                enable_mkldnn=False
            )
        
            TextDetection.__init__(self, self.rec_args)
    

    def detect(self, img):
        """
        Detect the text in the image
        Input: a image
        Output: A list of bounding boxes
        """
        ocr_res = []

        infer_img = img.copy()
        dt_boxes, _ = TextDetection.__call__(self, infer_img)

        tmp_res = [box.tolist() for box in dt_boxes]
        ocr_res.append(tmp_res)

        boxes = []
        for line in ocr_res[0]:
            boxes.append([[int(line[0][0]), int(line[0][1])], 
                          [int(line[1][0]), int(line[1][1])], 
                          [int(line[2][0]), int(line[2][1])], 
                          [int(line[3][0]), int(line[3][1])]])

        if len(boxes):
            return boxes
        else:
            return None

