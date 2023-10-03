import cv2
import yaml
import unidecode
import numpy as np
from src.OCR.extraction.text_extraction import TextExtraction
from utils.utility import config_collection_medicine, config_common_words_list, flatten_comprehension, config_collection_user_info, process_number

class TextExtractor(TextExtraction):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextExtractor.__instance__ == None:
            TextExtractor()
        return TextExtractor.__instance__

    def __init__(self, lang="vi"):
        if TextExtractor.__instance__ != None:
            raise Exception('Template Matching is a singleton!')
        else:
            TextExtractor.__instance__ = self

        TextExtraction.__init__(self, lang=lang)


    def extract_form_name(self, text, box):
        """
        Process the text: find form name on the image
        Input: the raw text, and the position of the text
        """
        form_name, is_form_name = self.find_form_name(text)
        if form_name:
            self.real_form_name = form_name
        '''
        Locate the position of the information if they exist
        '''
        if is_form_name:
            self.position_of_form_name.append(box)

        position_follow_up = {'follow_up_schedule': self.position_of_form_name}

        return position_follow_up, is_form_name


    def classify_form_name(self):

        return self.real_form_name
