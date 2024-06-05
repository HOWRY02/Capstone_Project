import os
import cv2
import yaml
import json
import imutils
import mysql.connector
from pydantic import BaseModel
from fastapi import FastAPI, Depends, File, UploadFile, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.table_creater import TableCreater
from src.info_extracter import InfoExtracter
from src.utils.utility import load_image, find_relative_position

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]

app = FastAPI(title='Template Creater')

app.mount("/static", StaticFiles(directory="src/WEB"), name="static")

templates = Jinja2Templates(directory="src/WEB/resources/views")

table_creater = TableCreater()
info_extracter = InfoExtracter()

if not os.path.exists('config/template'):
    os.makedirs('config/template')

if not os.path.exists('config/template_form'):
    os.makedirs('config/template_form')

# MySQL config
db_config = {
    'host': 'localhost',
    'user': 'admin',
    'password': '123456',
    'database': 'document_management'
}

class JSONData(BaseModel):
    data: str

def check_table_exists(table_name):
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return result is not None
    except Exception as e:
        print(f"Error checking table existence: {str(e)}")
        return False


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "imagePath": 'public/img/init_img.jpg'})


@app.get("/creatingTable")
async def creatingTableHome(request: Request):
    template = []
    return templates.TemplateResponse("create_table.html", {"request": request, "imagePath": 'public/img/init_img.jpg', "jsonData": template})


@app.get("/extractingInfo")
async def extractingInfoHome(request: Request):
    template = []
    return templates.TemplateResponse("extract_info.html", {"request": request, "imagePath": 'public/img/init_img.jpg', "jsonData": template})


@app.post("/creatingTable/rec")
async def creatingTable(request: Request,
                        imageInput: UploadFile = File()):

    image = load_image(imageInput.file)
    # image = imutils.resize(image, width=2000)
    template, status_code, [] = table_creater.create_table(image, is_visualize=True)

    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', image)

    return templates.TemplateResponse("create_table.html", {"request": request, "imagePath": 'public/img/temp_img.jpg', "jsonData": template})


@app.post("/extractingInfo/rec")
async def extractingInfo(request: Request,
                         imageInput: UploadFile = File()):
    
    image = load_image(imageInput.file)
    # image = imutils.resize(image, width=2000)
    result, status_code, [aligned] = info_extracter.extract_info(image, is_visualize=True)

    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', aligned)
    
    return templates.TemplateResponse("extract_info.html", {"request": request, "imagePath": 'public/img/temp_img.jpg', "jsonData": result})


@app.post("/confirm_and_create_table")
async def confirm_and_create_table(table_name: str):
    table_exists = check_table_exists(table_name)
    if table_exists:
        # If table exists, prompt user for confirmation
        return {"tableExists": True}
    else:
        return {"tableExists": False}


@app.post("/create_table_proceed")
async def create_table_proceed(data: JSONData):
    try:
        data_dict = json.loads(data.data)
        # sort data_dict
        data_dict.sort(key = lambda x: x['box'][1])

        for i, item in enumerate(data_dict):
            relative_position = find_relative_position(data_dict[i-1]['box'], item['box'])
            if relative_position == 1:
                data_dict[i]['box'][1] = min(data_dict[i-1]['box'][1], item['box'][1])
                data_dict[i-1]['box'][1] = min(data_dict[i-1]['box'][1], item['box'][1])

                data_dict[i]['box'][3] = max(data_dict[i-1]['box'][3], item['box'][3])
                data_dict[i-1]['box'][3] = max(data_dict[i-1]['box'][3], item['box'][3])

        data_dict.sort(key = lambda x: (x['box'][1], x['box'][0]))

        # Filter JSON data for items where class is "text"
        text_columns = [item['text'] for item in data_dict if (item['class'] == 'question' or item['class'] == 'date')]
        table_name = [item['text'] for item in data_dict if item['class'] == 'title'][0]

        # Generate MySQL table creation query
        columns = ', '.join(f"{col} VARCHAR(255)" for col in text_columns)
        query = f"CREATE TABLE {table_name} (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, {columns});"

        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        # Drop table if it exists
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        # Replace with your table creation SQL statement
        cursor.execute(query)
        db.commit()
        cursor.close()
        db.close()

        image = cv2.imread("src/WEB/public/img/temp_img.jpg", cv2.IMREAD_COLOR)
        cv2.imwrite(f"config/template/{table_name}.jpg", image)

        with open(f"config/template_form/{table_name}.json", 'w', encoding='utf-8') as outfile:
            json.dump(data_dict, outfile, ensure_ascii=True)

        return {"message": f"Table '{table_name}' created successfully."}
    except Exception as e:
        return {"message": f"Error creating table: {str(e)}."}


# FastAPI endpoint to insert data into MySQL table
@app.post("/insert_data")
async def insert_data(data: JSONData):
    try:
        data_dict = json.loads(data.data)

        # Filter JSON data for items where class is "text"
        text_columns = [item['text'] for item in data_dict if (item['class'] == 'answer' or item['class'] == 'date')]
        text_values = [item['ocr_text'] for item in data_dict if (item['class'] == 'answer' or item['class'] == 'date')]
        table_name = [item['text'] for item in data_dict if item['class'] == 'title'][0]

        # Generate MySQL table creation query
        columns = ', '.join(f"{col}" for col in text_columns)
        values = ', '.join(f"'{val}'" for val in text_values)
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()

        cursor.execute(query)
        db.commit()

        cursor.close()
        db.close()

        return {"message": "Data inserted successfully"}
    except Exception as e:
        return {"message": f"Error inserting data: {str(e)}"}


# Run the application (optional, for development purposes)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
