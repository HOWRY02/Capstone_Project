import re
import unidecode
import datefinder
from datetime import datetime
import dateutil.parser as dparser
from thefuzz import fuzz, process

class TextExtraction(object):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextExtraction.__instance__ == None:
            TextExtraction()
        return TextExtraction.__instance__

    def __init__(self, lang="vi"):
        if TextExtraction.__instance__ != None:
            raise Exception('Template Matching is a singleton!')
        else:
            TextExtraction.__instance__ = self

            self.real_form_name = None
            self.position_of_form_name = []


    def find_form_name(self, text):

        form_name = None
        is_form_name = False
        lower_text = text.lower()
        ascii_text = unidecode.unidecode(lower_text)

        match_str = fuzz.partial_ratio(ascii_text, "don")
        if match_str > 90:
            ascii_text_split = ascii_text.split()
            print(ascii_text_split)
            if len(ascii_text_split) > 3:
                form_name = text
                is_form_name = True

        return form_name, is_form_name


    def reset_info(self):
        """
        Reset all infor of user after sending result to api
        """
        self.real_form_name = None
        self.position_of_form_name = []
