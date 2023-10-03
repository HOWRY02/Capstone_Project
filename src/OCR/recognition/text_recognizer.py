import os
import sys
import time
from PIL import Image
from argparse import Namespace
from src.OCR.recognition.text_recognition import TextRecognition

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

import utility as utility

def sort_index(lst, rev=True):
    index = range(len(lst))
    s = sorted(index, reverse=rev, key=lambda i: lst[i])
    return s

class TextRecognizer(TextRecognition):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextRecognizer.__instance__ == None:
            TextRecognizer()
        return TextRecognizer.__instance__

    def __init__(self, lang="en"):
        if TextRecognizer.__instance__ != None:
            raise Exception('Text Recognizer is a singleton!')
        else:
            TextRecognizer.__instance__ = self

            self.rec_args = Namespace(
                image_dir = "src/img_test_inbody.jpeg",
                rec_algorithm="SVTR_LCNet",
                rec_model_dir="model/recognition_model/en_PP-OCRv3_rec_infer",
                rec_image_inverse=True,
                rec_image_shape="3, 48, 320",
                rec_batch_num=6,
                max_text_length=25,
                rec_char_dict_path="src/OCR/ppocr/utils/en_dict.txt",
                use_space_char=True,
                vis_font_path="./doc/fonts/simfang.ttf",
                drop_score=0.5,
                use_onnx = False,
                benchmark = False,
                use_gpu = True,
                use_xpu = False,
                use_npu = False,
                ir_optim = True,
                use_tensorrt = False,
                min_subgraph_size = 15,
                precision = "fp32",
                gpu_mem = 500,
                gpu_id = 0
            )
            self.lang = lang
            TextRecognition.__init__(self, self.rec_args)


    def change_language(self, lang):
        if self.lang != lang:
            self.lang = lang
            if lang == "en":
                self.rec_args.rec_model_dir = "model/recognition_model/en_PP-OCRv3_rec_infer"
                self.rec_args.rec_char_dict_path="src/OCR/ppocr/utils/en_dict.txt"
                self.rec_args.rec_algorithm="SVTR_LCNet"
            elif lang == "vi":
                self.rec_args.rec_model_dir = "model/recognition_model/vi_PP-OCRv3_rec_infer"
                self.rec_args.rec_char_dict_path="src/OCR/ppocr/utils/vi_vietnam.txt"
                self.rec_args.rec_algorithm="SVTR"
            TextRecognition.__init__(self, self.rec_args)

    def recognize(self,img_list):
        args = vars(self.rec_args)
        rec_res, time_pr = TextRecognition.__call__(self, [img_list])
        rec_res = rec_res[0][0]

        return rec_res

