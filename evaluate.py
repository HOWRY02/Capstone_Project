import os
import re
import cv2
import json
import copy
import pandas as pd
from tqdm import tqdm
from time import perf_counter
from src.info_extracter import InfoExtracter
from src.utils.utility import load_image, hconcat_resize

# Create an instance of the Singleton class
info_extracter = InfoExtracter()

# Test directory
test_dir = 'data/printed_file'

if not os.path.exists('result/info_extraction_image'):
    os.makedirs('result/info_extraction_image')

is_visualize = True

def main():
    test_images = os.listdir(test_dir)
    test_images.sort(key = lambda file_name: int(re.sub(r"[^0-9]", "", file_name)))
    # test_images.sort(key = lambda file_name: int(re.sub(r"[^0-9]", "", re.sub("en", "100", file_name))))
    for image in tqdm(test_images):
        try:
            img = load_image(test_dir + '/' + image)

            template, status_code, [aligned] = info_extracter.extract_info(img, is_visualize)

            if is_visualize:
                cv2.imwrite(f'result/info_extraction_image/{image.split(".")[0]}.png', aligned)

        except Exception as e:
            print(image)
            print(e)
            pass

if __name__ == '__main__':
    main()
