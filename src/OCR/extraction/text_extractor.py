import os
import sys

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

from src.OCR.extraction.text_extraction import TextExtraction

class TextExtractor(TextExtraction):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if TextExtractor.__instance__ == None:
            TextExtractor()
        return TextExtractor.__instance__

    def __init__(self):
        if TextExtractor.__instance__ != None:
            raise Exception('This class is a singleton!')
        else:
            TextExtractor.__instance__ = self

        TextExtraction.__init__(self)
        self.real_form_name = None
        self.real_position_of_form_name = None


    def extract_form_name(self, titles):
        """
        Process the text: find form name on the image
        Input: the raw text, and the position of the text
        """
        for i, text in enumerate(titles['text']):
            form_name = self.find_form_name(text)
            position_of_form_name = titles['box'][i]
            if form_name is not None:
                self.real_form_name = form_name
                self.real_position_of_form_name = position_of_form_name

        return self.real_form_name, self.real_position_of_form_name


    def extract_column_name(self, question_texts):
        """
        Process the text: find form name on the image
        Input: the raw text, and the position of the text
        """
        for i, text in enumerate(question_texts):
            question_texts[i] = self.find_column_name(text)
            
        return question_texts
