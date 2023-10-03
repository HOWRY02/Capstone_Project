import os
import pandas as pd
import json
import copy
from tqdm import tqdm
from time import perf_counter
from src.paper_ocr import PaperOcrParser
from src.utils.utility import load_image, hconcat_resize
import re
import cv2
from time import perf_counter
# Create an instance of the Singleton class
extractor = PaperOcrParser()

# Test directory
test_dir = 'src/data'

# Create new template {group_key : value}
# time_table = {"Name":  [],
#               "Language":  [],
#               "First detection":  [],
#               "Number of detected box (boxes)":  [],
#               "Get text image":  [], 
#               "Recognize":  [], 
#               "Extract follow up":  [], 
#               "Capture common words":  [],
#               "Detect lines":  [],
#               "Recognize values":  [],
#               "Total":  []}

# time_table = {"Name" : [],
#               "Language": [],
#               "Total" : []}

# if not os.path.exists(f'src/data_result'):
#     os.makedirs(f'src/data_result')

if not os.path.exists(f'src/data_result_json'):
    os.makedirs(f'src/data_result_json')


def main():
    test_images = os.listdir(test_dir) 
    # test_images.sort(key = lambda file_name: int(re.sub(r"[^0-9]", "", file_name)))
    for image in tqdm(test_images):
        # img = cv2.imread(test_dir + '/' + image)
        # cv2.imwrite(test_dir + '/' + image, img)
        try:
            start = perf_counter()
            img = load_image(test_dir + '/' + image)

            # language = image.split("_")[0]
            # language = "vi1" if language != "en" else "en"

            language = "vi1"
            extractor.change_language(language)
            # performance = [image, language]
            result, status_code, boxes_img = extractor.extract_info(img)
            # performance = performance + perf
        
            # cv2.imwrite(f'src/data_result/{image.split(".")[0]}_result.png', save_img)

            # with open(f'src/data_result_json/{image.split(".")[0]}_result.json', 'w', encoding='utf-8') as outfile:
            #     json.dump(result, outfile, ensure_ascii=False)

            with open(f'src/data_result_json/{image.split(".")[0]}_result.json', 'w', encoding='utf-8') as outfile:
                json.dump(result, outfile, ensure_ascii=False)

            # time_table["Name"].append(image)
            # time_table["Language"].append("vi1")
            # time_table["Total"].append(round(perf_counter() - start, 2))

            # for (i, key) in enumerate(time_table.keys()):
            #     time_table[key].append(performance[i])
        except Exception as ex:
            print(image)
            print(ex)
            pass

    # df = pd.DataFrame(time_table)
    # df.to_csv('test_result_time.csv')


if __name__ == '__main__':
    main()
