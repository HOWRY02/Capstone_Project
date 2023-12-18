import cv2
import yaml
import json
import mysql.connector
from pydantic import BaseModel
from fastapi import FastAPI, Depends, File, UploadFile, Form, Request
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

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="123456",
    database="document_management"
)

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
    template, status, [image, form_img] = creater.create(img, False)

    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', image)

    with open('result/template.json', 'w', encoding='utf-8') as outfile:
        json.dump(template, outfile, ensure_ascii=False)

    return templates.TemplateResponse("create_table.html", {"request": request, "imagePath": 'public/img/temp_img.jpg', "jsonData": template})


@app.post("/create")
async def create(data: JSONData):
    try:
        # cursor = db.cursor()
        # cursor.execute(f"CREATE TABLE IF NOT EXISTS new_table ({data.data})")
        # db.commit()
        data_dict = json.loads(data.data)
        print(data_dict)
        return {"message": "Table created successfully"}
    except Exception as e:
        return {"message": f"Error creating table: {str(e)}"}


@app.post("/extractingInfo/rec")
async def extractingInfo(request: Request,
                         imageInput: UploadFile = File()):
    
    return templates.TemplateResponse("extract_info.html", {"request": request})

