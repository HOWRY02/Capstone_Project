import os
import pandas as pd
from thefuzz import fuzz
import yaml
import re
from tqdm import tqdm
from time import perf_counter
# from src.prescriptionOCR import PrescriptionParser

import cv2
# Create an instance of the Singleton class
# extractor = PrescriptionParser()

# Result directory
test_dir = 'src/data_result_json'

# Ground truth directory
ground_truth_dir = 'src/data_result_ground_truth'

save = {"name" : [],
        "medicine_name": [],
        "duration_value": [],
        "duration_unit": [],
        "strength_value": [],
        "strength_unit": [],
        "quantity": [],
        "dosage": [],
        "route": [],
        "form": [],
        "medication_timing": []}

def check_same(str1, str2):
    fuzz_threshold = 85.0
    try:
        if str1 is None and str2 is None:
            return True
        elif (str1 is None and str2 is not None) or (str1 is not None and str2 is None):
            return False
        else:
            return True if fuzz.partial_ratio(str(str1), str(str2)) >= fuzz_threshold else False

    except Exception as ex:
        print(str1, str2)
        return False

def main():
    test_results = os.listdir(test_dir) 
    test_results.sort(key = lambda file_name: int(re.sub(r"[^0-9]", "", file_name)))
    for _json in tqdm(test_results):
        with open(test_dir + "/" + _json) as yaml_file:
            res = yaml.safe_load(yaml_file)
        with open(ground_truth_dir + "/" + _json) as yaml_file:
            gt = yaml.safe_load(yaml_file)
        if len(res["medicine"]) == len(gt["medicine"]):
            s = {"medicine_name": 0,
                "duration_value": 0,
                "duration_unit": 0,
                "strength_value": 0,
                "strength_unit": 0,
                "quantity": 0,
                "dosage": 0,
                "route": 0,
                "form": 0,
                "medication_timing": 0}

            num_med = len(res["medicine"])

            for i in range(num_med):
                for key in res["medicine"][i].keys():
                    if key == "duration":
                        if check_same(res["medicine"][i]["duration"]["value"], gt["medicine"][i]["duration"]["value"]):
                            s["duration_value"] += 1
                        if check_same(res["medicine"][i]["duration"]["unit"], gt["medicine"][i]["duration"]["unit"]):
                            s["duration_unit"] += 1
                    elif key == "strength":
                        if check_same(res["medicine"][i]["strength"]["value"], gt["medicine"][i]["strength"]["value"]):
                            s["strength_value"] += 1
                        if check_same(res["medicine"][i]["strength"]["unit"], gt["medicine"][i]["strength"]["unit"]):
                            s["strength_unit"] += 1
                    elif key == "dosage":
                        dosage_count = 0
                        for d_key in res["medicine"][i]["dosage"]:
                            if check_same(res["medicine"][i]["dosage"][d_key], gt["medicine"][i]["dosage"][d_key]):
                                dosage_count += 1
                        if dosage_count == 5:
                            s["dosage"] += 1
                    else:
                        if check_same(res["medicine"][i][key], gt["medicine"][i][key]):
                            if key != "instruction":    
                                s[key] += 1


            for key in s.keys():
                save[key].append(round(s[key] * 100.0 / num_med, 2))
            save["name"].append(re.sub("_result.json", "", _json))
        else:
            s = {"medicine_name": 0,
                "duration_value": 0,
                "duration_unit": 0,
                "strength_value": 0,
                "strength_unit": 0,
                "quantity": 0,
                "dosage": 0,
                "route": 0,
                "form": 0,
                "medication_timing": 0}
            for j in range(len(gt["medicine"])):
                for i in range(len(res["medicine"])):
                    if check_same(res["medicine"][i]["medicine_name"], gt["medicine"][j]["medicine_name"]):
                        for key in res["medicine"][i].keys():
                            if key == "duration":
                                if check_same(res["medicine"][i]["duration"]["value"], gt["medicine"][j]["duration"]["value"]):
                                    s["duration_value"] += 1
                                if check_same(res["medicine"][i]["duration"]["unit"], gt["medicine"][j]["duration"]["unit"]):
                                    s["duration_unit"] += 1
                            elif key == "strength":
                                if check_same(res["medicine"][i]["strength"]["value"], gt["medicine"][j]["strength"]["value"]):
                                    s["strength_value"] += 1
                                if check_same(res["medicine"][i]["strength"]["unit"], gt["medicine"][j]["strength"]["unit"]):
                                    s["strength_unit"] += 1
                            elif key == "dosage":
                                dosage_count = 0
                                for d_key in res["medicine"][i]["dosage"]:
                                    if check_same(res["medicine"][i]["dosage"][d_key], gt["medicine"][j]["dosage"][d_key]):
                                        dosage_count += 1
                                if dosage_count == 5:
                                    s["dosage"] += 1
                            else:
                                if check_same(res["medicine"][i][key], gt["medicine"][j][key]):
                                    if key != "instruction":    
                                        s[key] += 1
                        break
            for key in s.keys():
                save[key].append(round(s[key] * 100.0 / len(gt["medicine"]), 2))
            save["name"].append(re.sub("_result.json", "", _json))
    df = pd.DataFrame(save)
    df.to_csv('test_result.csv')

if __name__ == '__main__':
    main()
