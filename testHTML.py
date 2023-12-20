import cv2
import yaml
import json
import mysql.connector
from pydantic import BaseModel
from fastapi import FastAPI, Depends, File, UploadFile, Form, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.template_creater import TemplateCreater
from src.utils.utility import load_image

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]
app = FastAPI(title='Template Creater')

app.mount("/static", StaticFiles(directory="src/WEB"), name="static")

templates = Jinja2Templates(directory="src/WEB/resources/views")

creater = TemplateCreater()  # create an instance of the Singleton class

is_visualize = True

# MySQL config
db_config = {
    'host': 'localhost',
    'user': 'admin',
    'password': '123456',
    'database': 'document_management'
}

class JSONData(BaseModel):
    data: str

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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

    img = load_image(imageInput.file)
    template, status, [image, form_img] = creater.create(img, is_visualize)

    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', image)

    with open('result/template.json', 'w', encoding='utf-8') as outfile:
        json.dump(template, outfile, ensure_ascii=False)

    if is_visualize:
        cv2.imwrite(f'result/form_img.jpg', form_img)

    return templates.TemplateResponse("create_table.html", {"request": request, "imagePath": 'public/img/temp_img.jpg', "jsonData": template})


@app.post("/extractingInfo/rec")
async def extractingInfo(request: Request,
                         imageInput: UploadFile = File()):
    
    return templates.TemplateResponse("extract_info.html", {"request": request})


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
        data_dict.sort(key = lambda x: (x['box'][1], x['box'][0]))

        # Filter JSON data for items where class is "text"
        text_columns = [item['text'] for item in data_dict if item['class'] != 'title']
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

        with open(f"config/template_form/{table_name}.json", 'w', encoding='utf-8') as outfile:
            json.dump(data_dict, outfile, ensure_ascii=True)

        return {"message": f"Table '{table_name}' created successfully."}
    except Exception as e:
        return {"message": f"Error creating table: {str(e)}."}
