import yaml

common_words_list = {"vi": {"units":['ml', 'mg', 'ui', 'mcg', 'g', 'omg'], 
                      "time":['sang', 'trua', 'chieu', 'toi'], 
                      "frequency":['moi', 'lan'], 
                      "formulation_type":['vien', 'goi', 'chai', 'but', 'ong', 'bo', 'hop', 'lo'], 
                      "route":['uong', 'tiem', 'xit', 'kho', 'rua'], 
                      "miscellaneous_words":['luong', 'thoi gian']}, 
                     "en": {"units":['ml', 'mg', 'ui', 'mcg', 'g'], 
                      "time":['afternoon', 'night', 'morning', 'day', 'month', 'week', 'evening'], 
                      "frequency":['times', 'once', 'twice', 'thrice', 'qid', 'daily', 'q4h', 'q6h', 'q8h', 'prn'], 
                      "formulation_type":['tab', 'cap', 'tablet', 'capsule', 'cream', 'drops', 'ointment', 'gel', 'syrup', 'bottle'], 
                      "route":['oral'], 
                      "miscellaneous_words":['rx', 'breakfast', 'lunch', 'meal', 'after', 'before', 'total']}}

collection_medicine = {"vi": {"collection_dosage":['sang', 'trua', 'chieu', 'toi', 'lan', 'luc', 'truoc', 'sau', 'trong'], 
                              "dosage_cases":['sang', 'trua', 'chieu', 'toi'], 
                              "collection_timing":['uong luc', 'truoc an', 'sau an', 'trong bua an'],
                              "collection_duration":['ngay', 'thang', 'tuan']}, 
                       "en": {"collection_dosage":['after', 'before', 'qid', 'daily', 'q4h', 'q6h', 'q8h', 'prn', 'afternoon', 'night', 
                                                   'morning', 'evening', 'aft', 'eve', 'times', 'day'], 
                              "dosage_cases":['morning', 'noon', 'afternoon', 'night', 'evening'], 
                              "collection_timing":['before food', 'after food', 'before meal', 'after meal'], 
                              "collection_duration":['day', 'month', 'week']}}

collection_user_info = {"vi": {"collection_name":['ky ghi ro ho ten', 'ho va ten', 'ho ten', 'ten benh nhan'], 
                               "collection_age":['tuoi', 'nam sinh', 'ngay sinh'], 
                               "collection_gender":['phai', 'nam / nu', 'gioi tinh'], 
                               "collection_follow_up":['tai kham']}, 
                        "en": {"collection_name":['name'], 
                               "collection_age":['age', 'date of birth', 'dob', 'birthdate'], 
                               "collection_gender":['sex', 'gender'], 
                               "collection_follow_up":['follow up']}}

with open('config/common_words_list.yaml', 'w', encoding='utf-8') as outfile:
    yaml.dump(common_words_list, outfile, sort_keys=False, allow_unicode=True)

with open('config/collection_medicine.yaml', 'w', encoding='utf-8') as outfile:
    yaml.dump(collection_medicine, outfile, sort_keys=False, allow_unicode=True)

with open('config/collection_user_info.yaml', 'w', encoding='utf-8') as outfile:
    yaml.dump(collection_user_info, outfile, sort_keys=False, allow_unicode=True)
