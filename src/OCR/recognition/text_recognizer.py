import os
import sys
import torch

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

from src.OCR.recognition.tool.config import Cfg
from src.OCR.recognition.tool.predictor import Predictor


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
            raise Exception('This class is a singleton!')
        else:
            TextRecognizer.__instance__ = self

            # load VietOCR
            # 2 lines below are similar
            # fisrt line: download weights into a temp path
            # second line: use the available weights in path model/vietocr_model

            # # self.config = Cfg.load_config_from_name('vgg_seq2seq')
            # self.config = Cfg.load_config_from_file('model/recognition_model/vi_vietocr_vgg19_seq2seq/vgg-seq2seq.yml')
            # # self.config['cnn']['pretrained'] = True                        # torchvision < 0.13
            # self.config['cnn']['weights'] = 'VGG19_BN_Weights.IMAGENET1K_V1' # torchvision >= 0.13
            # self.config['device'] = 'cuda:0' # cpu or use 'cuda:0'
            # self.detector = Predictor(self.config)

            self.config = Cfg.load_config_from_file('model/recognition_model/vi_vietocr_vgg19_seq2seq/vgg-seq2seq.yml')
            self.config['pretrain'] = 'model/recognition_model/vi_vietocr_vgg19_seq2seq/vgg_seq2seq.pth'
            self.config['weights'] = 'model/recognition_model/vi_vietocr_vgg19_seq2seq/vgg_seq2seq.pth'
            self.config['predictor']['beamsearch'] = False
            print('Text recognition uses', self.device)
            self.config['device'] = self.device
            self.detector = Predictor(self.config)

    def recognize(self, img):
        text = self.detector.predict(img)
        return text
    
    @property
    def device(self):
        # Check torch available
        if torch.cuda.is_available():
            return 'cuda:0'
        else:
            return 'cpu'
    