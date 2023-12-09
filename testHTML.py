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

templates = Jinja2Templates(directory="src/WEB")

creater = TemplateCreater()  # create an instance of the Singleton class

@app.get("/")
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# input is image link
@app.post("/extracting")
async def extracting(request: Request,
                     imageInput: UploadFile = File()):

    extension = imageInput.filename.split(".")[-1] in ("jpg", "jpeg", "png")

    info = {}
    result = {}
    if not extension:
        result = JSONResponse(status_code = 460, 
                content = {"status_code": '460', 
                        "message": STATUS['460'],
                        "result": info
                        })
    else:
        img = load_image(imageInput.file)
        template, status, [form_img] = creater.create(img, False)
        result = JSONResponse(status_code = int(status), 
                content = {"status_code": status, 
                        "message": STATUS[status],
                        "result": template
                        })
        
        with open('src/result/template.json', 'w', encoding='utf-8') as outfile:
            json.dump(template, outfile, ensure_ascii=False)
        
    return templates.TemplateResponse("index.html", {"request": request,"imageCanvas": imageInput.filename,"jsonData": template})