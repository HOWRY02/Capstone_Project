import os
import sys
from PIL import Image

from detection import Detection
from argparse import Namespace

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'


class Detector(Detection):
    def __init__(self, args):

        self.args = Namespace(
            det_algorithm = 'DB', 
            use_gpu = True, 
            use_xpu = False, 
            use_npu = False, 
            gpu_mem = 500, 
            gpu_id = 0, 
            det_db_thresh = 0.3, 
            det_db_box_thresh = 0.6, 
            det_db_unclip_ratio = 1.5, 
            max_batch_size = 10, 
            use_onnx = False, 
            benchmark = False
        )

    def detector(self, img):
        dt_boxes, time_pr = self.__call__(img)
        return dt_boxes
