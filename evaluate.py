import os
import re
import cv2
import json
import copy
import pandas as pd
from tqdm import tqdm
from time import perf_counter
from src.paper_ocr import PaperOcrParser
from src.utils.utility import load_image, hconcat_resize

# Create an instance of the Singleton class
extractor = PaperOcrParser()

# Test directory
test_dir = 'src/data/written_file'

if not os.path.exists(f'src/result_json'):
    os.makedirs(f'src/result_json')

is_visualize = False

def main():
    test_images = os.listdir(test_dir)
    test_images.sort(key = lambda file_name: int(re.sub(r"[^0-9]", "", file_name)))
    # test_images.sort(key = lambda file_name: int(re.sub(r"[^0-9]", "", re.sub("en", "100", file_name))))
    for image in tqdm(test_images):
        try:
            img = load_image(test_dir + '/' + image)

            info, status, [boxes_img,layout_img] = extractor.extract_info(img, is_visualize)

            with open(f'src/result_json/{image.split(".")[0]}_result.json', 'w', encoding='utf-8') as outfile:
                json.dump(info, outfile, ensure_ascii=False)

            if is_visualize:
                # cv2.imwrite(f'src/data_result/{image.split(".")[0]}_result.png', boxes_img)
                cv2.imwrite(f'src/result_layout_analysis/{image.split(".")[0]}_result.png', layout_img)

        except Exception as e:
            print(image)
            print(e)
            pass

if __name__ == '__main__':
    main()
