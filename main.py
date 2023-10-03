## here is implement REST API
import cv2
import yaml
import json
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Union
from pydantic import BaseModel
from typing_extensions import Annotated
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, File, UploadFile, Form

from src.paper_ocr import PaperOcrParser
from src.utils.utility import load_image

is_visuzlize = True

def read_imagefile(file) -> Image.Image:
    image = Image.open(BytesIO(file))
    return image

with open("./config/doc_config.yaml", "r") as f:
    doc_config = yaml.safe_load(f)
STATUS = doc_config["status"]
app = FastAPI(title='Prescription Extractor')

class Request(BaseModel):
    image: Annotated[UploadFile, File()]
    language: str = Form(..., description = "vi / en")

extractor = PaperOcrParser()  # create an instance of the Singleton class

# Define the default route 
@app.get("/")
async def root(singleton_instance: PaperOcrParser = Depends(lambda: extractor)):
    return {"message": "Welcome to Prescription Extractor!", "instance_id": id(singleton_instance)}

# input is image link
@app.post("/prescription/rec")
async def extracting(image: Annotated[UploadFile, File(...)],
                     language: str = Form(..., description = "vi / vi1 / en")
                    ):

    extension = image.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    language_code = language in ("vi", "vi1", "en")
    info = {}
    result = {}
    if not language_code:
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
        extractor.change_language(language)
        info, status, boxes_img = extractor.extract_info(img)
        result = JSONResponse(status_code = int(status), 
                content = {"status_code": status, 
                        "message": STATUS[status],
                        "result": info
                        })
        
        with open('src/result/result.json', 'w', encoding='utf-8') as outfile:
            json.dump(info, outfile, ensure_ascii=False)
        
        if is_visuzlize:
            cv2.imwrite(f'src/result/boxes_img.png', boxes_img)
        
    return result

