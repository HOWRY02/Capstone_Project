import os
import sys
import unidecode
from thefuzz import fuzz, process

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

from src.utils.utility import config_form_name_list, config_name_of_column, flatten_comprehension

class TextExtraction(object):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextExtraction.__instance__ == None:
            TextExtraction()
        return TextExtraction.__instance__

    def __init__(self):
        if TextExtraction.__instance__ != None:
            raise Exception('Template Matching is a singleton!')
        else:
            TextExtraction.__instance__ = self
            self.form_name_list = config_form_name_list()
            self.column_name_dict = config_name_of_column()
            self.real_form_name = None
            self.position_of_form_name = []


    def find_form_name(self, text):

        form_name = None
        lower_text = text.lower()

        matches_str = process.extract(lower_text, self.form_name_list, scorer=fuzz.token_sort_ratio)
        # print(matches_str)
        # if matches_str[0][1] > 80:
        form_name = matches_str[0][0]

        return form_name
    

    def find_column_name(self, text):

        column_name = text
        lower_text = text.lower()
        ascii_text = unidecode.unidecode(lower_text)

        matches_str = process.extract(ascii_text, flatten_comprehension(self.column_name_dict.values()), 
                                      scorer=fuzz.token_sort_ratio)
        if matches_str[0][1] > 90:
            for key, value in self.column_name_dict.items():
                if matches_str[0][0] in value:
                    column_name = key

        return column_name


    def reset_info(self):
        """
        Reset all infor of user after sending result to api
        """
        self.real_form_name = None
        self.position_of_form_name = []
