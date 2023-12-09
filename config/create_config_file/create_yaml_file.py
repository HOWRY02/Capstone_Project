import yaml

form_name_list = {"form_name":['đơn xin miễn thi',
                               'đơn xin bảo lưu điểm',
                               'đơn xin cấp bản sao từ sổ gốc bằng tốt nghiệp',
                               'đơn xin chuyển điểm',
                               'đơn xin chuyển điểm ngoại ngữ',
                               'đơn xin xét chuyển trình độ đào tạo',
                               'đơn xin học môn thay thế',
                               'đơn xin miễn thi anh văn đầu ra',
                               'đơn xin nhận điểm i (điểm chưa hoàn tất)']}

name_of_column = {'ho ten':['ho ten sinh vien', 'toi ten', 'em la', 'ho va ten sinh vien'],
                  'mssv':['ma sv', 'mssv', 'ma so sv', 'ma so sinh vien'],
                  'dien thoai':['dien thoai', 'so dt lien he'],
                  'lop':['lop'],
                  'khoa':['khoa']}


with open('config/form_name_list.yaml', 'w', encoding='utf-8') as outfile:
    yaml.dump(form_name_list, outfile, sort_keys=False, allow_unicode=True)

with open('config/name_of_column.yaml', 'w', encoding='utf-8') as outfile:
    yaml.dump(name_of_column, outfile, sort_keys=False, allow_unicode=True)
