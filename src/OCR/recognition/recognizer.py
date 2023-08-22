import os
import sys
from PIL import Image

from recognition import Recognition
from argparse import Namespace

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'


class Recognizer(Recognition):
    def __init__(self, args):

        self.args = Namespace(
            
        )


