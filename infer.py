import cv2
import yaml
import json
from PIL import Image
from io import BytesIO
from pydantic import BaseModel
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, File, UploadFile, Form

from src.table_creater import TemplateCreater
from src.utils.utility import load_image

is_visualize = False

def read_imagefile(file) -> Image.Image:
    image = Image.open(BytesIO(file))
    return image

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]
app = FastAPI(title='Template Creater')

class Request(BaseModel):
    image: Annotated[UploadFile, File()]

creater = TemplateCreater()  # create an instance of the Singleton class

# Define the default route 
@app.get("/")
async def root(singleton_instance: TemplateCreater = Depends(lambda: creater)):
    return {"message": "Welcome to Template Creater!", "instance_id": id(singleton_instance)}

# input is image link
@app.post("/template/rec")
async def extracting(image: Annotated[UploadFile, File(...)],
                     visualize: str = Form(..., description = "y/n")):

    extension = image.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    visualize_code = visualize in ('y', 'n')
    info = {}
    result = {}
    if not visualize_code:
        result = JSONResponse(status_code = 474, 
                content = {"status_code": '474', 
                        "message": STATUS['474'],
                        "result": info
                        })
    elif not extension:
        result = JSONResponse(status_code = 460, 
                content = {"status_code": '460', 
                        "message": STATUS['460'],
                        "result": info
                        })
    else:
        img = load_image(image.file)
        if visualize == 'y':
            is_visualize = True
        else:
            is_visualize = False
        template, status, [form_img] = creater.create_table(img, is_visualize)
        result = JSONResponse(status_code = int(status), 
                content = {"status_code": status, 
                        "message": STATUS[status],
                        "result": template
                        })
        
        with open('src/result/template.json', 'w', encoding='utf-8') as outfile:
            json.dump(template, outfile, ensure_ascii=False)

        if is_visualize:
            cv2.imwrite(f'src/result/form_img.jpg', form_img)
        
    return result

