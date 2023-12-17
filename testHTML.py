import cv2
import yaml
import json
from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, File, UploadFile, Form, Request

from src.template_creater import TemplateCreater
from src.utils.utility import load_image

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]
app = FastAPI(title='Template Creater')

app.mount("/static", StaticFiles(directory="src/WEB"), name="static")

templates = Jinja2Templates(directory="src/WEB/resources/views")

creater = TemplateCreater()  # create an instance of the Singleton class

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/findingColumns")
async def findingColumns(request: Request):
    template = []
    return templates.TemplateResponse("find_columns.html", {"request": request, "imagePath": 'public/img/init_img.jpg', "jsonData": template})


@app.get("/extractingInfo")
async def extractingInfo(request: Request):
    template = []
    return templates.TemplateResponse("extract_info.html", {"request": request, "imagePath": 'public/img/init_img.jpg', "jsonData": template})


@app.post("/findingColumns/rec")
async def findingColumns(request: Request,
                         imageInput: UploadFile = File()):

    img = load_image(imageInput.file)
    template, status, [image, form_img] = creater.create(img, False)

    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', image)

    with open('result/template.json', 'w', encoding='utf-8') as outfile:
        json.dump(template, outfile, ensure_ascii=False)

    return templates.TemplateResponse("find_columns.html", {"request": request, "imagePath": 'public/img/temp_img.jpg', "jsonData": template})

# @app.post("/creatingTable/rec")
# async def creatingTable(request: Request, templateDisplay: str):
#     print(templateDisplay)
#     return templates.TemplateResponse("extract_info.html", {"request": request, })
@app.post("/creatingTable/rec")
async def create_table(request: Request):
    # if templateDisplay:
    #     received_data = templateDisplay
    # else:
    received_data = "abc"
    # Process received_data as needed
    # return {"message": "Received data", "received_data": received_data}
    return templates.TemplateResponse("create_table.html", {"request": request, "templateDisplay": received_data})

@app.post("/extractingInfo/rec")
async def extractingInfo(request: Request,
                     imageInput: UploadFile = File()):
    
    return templates.TemplateResponse("extract_info.html", {"request": request})


