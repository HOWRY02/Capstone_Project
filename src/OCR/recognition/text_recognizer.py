import os
import sys

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

from src.OCR.recognition.tool.config import Cfg
from src.OCR.recognition.tool.predictor import Predictor

# os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

class TextRecognizer():
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextRecognizer.__instance__ == None:
            TextRecognizer()
        return TextRecognizer.__instance__

    def __init__(self):
        if TextRecognizer.__instance__ != None:
            raise Exception('Text Recognizer is a singleton!')
        else:
            TextRecognizer.__instance__ = self

            # load VietOCR
            # 2 lines below are similar
            # fisrt line: download weights into a temp path
            # second line: use the available weights in path model/vietocr_model

            # self.config = Cfg.load_config_from_name('vgg_seq2seq')
            self.config = Cfg.load_config_from_file('model/recognition_model/vi_vietocr_vgg19_seq2seq/vgg-seq2seq.yml')
            # self.config['cnn']['pretrained'] = True                        # torchvision < 0.13
            self.config['cnn']['weights'] = 'VGG19_BN_Weights.IMAGENET1K_V1' # torchvision >= 0.13
            self.config['device'] = 'cpu' # or use 'cuda:0'
            self.detector = Predictor(self.config)

    def recognize(self, img):
        text = self.detector.predict(img)
        return text
    
    