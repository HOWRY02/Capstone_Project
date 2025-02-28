import os
import cv2
import json
import imutils
import uvicorn
import subprocess
import mysql.connector
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from src.table_creater import TableCreater
from src.info_extracter import InfoExtracter
from src.utils.utility import load_image, find_relative_position, format_data_dict


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
    scale_factor = 1.0
    return templates.TemplateResponse("create_table.html", {"request": request,
                                                            "imagePath": 'public/img/init_img.jpg',
                                                            "jsonData": template,
                                                            "scaleFactor": scale_factor})


@app.get("/extractingInfo")
async def extractingInfoHome(request: Request):
    template = []
    return templates.TemplateResponse("extract_info.html", {"request": request,
                                                            "imagePath": 'public/img/init_img.jpg',
                                                            "jsonData": template})


@app.get("/showingData")
async def extractingInfoHome(request: Request):
    return templates.TemplateResponse("show_data.html", {"request": request})


def scale_box(template: list, scale_factor):
    new_template = template.copy()
    for i in range(len(new_template)):
        box = [int(x * scale_factor) for x in new_template[i]['box']]
        new_template[i]['box'] = box
        if 'answer_text' in new_template[i].keys():
            for answer_element in new_template[i]['answer_text']:
                answer_box = [int(x * scale_factor) for x in answer_element['box']]
                answer_element['box'] = answer_box

    return new_template

@app.post("/creatingTable/rec")
async def creatingTable(request: Request,
                        imageInput: UploadFile = File()):
    global scale_factor
    image = load_image(imageInput.file)
    template, status_code, [] = table_creater.create_table(image, is_visualize=True)

    # save the raw image
    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', image)
    # save the resized image
    scale_factor = 1000 / image.shape[1]
    resized_img = imutils.resize(image, width=1000)
    cv2.imwrite(f'src/WEB/public/img/resized_img.jpg', resized_img)
    # apply scale factor for display on the web
    template = scale_box(template, scale_factor)

    return templates.TemplateResponse("create_table.html", {"request": request,
                                                            "imagePath": 'public/img/resized_img.jpg',
                                                            "jsonData": template,
                                                            "scaleFactor": scale_factor})


@app.post("/extractingInfo/rec")
async def extractingInfo(request: Request,
                         imageInput: UploadFile = File()):
    global scale_factor
    image = load_image(imageInput.file)
    result, status_code, [aligned] = info_extracter.extract_info(image, is_visualize=True)

    # save the aligned image
    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', aligned)
    # save the resized image
    scale_factor = 1000 / aligned.shape[1]
    resized_img = imutils.resize(aligned, width=1000)
    cv2.imwrite(f'src/WEB/public/img/resized_img.jpg', resized_img)
    # apply scale factor for display on the web
    result = scale_box(result, scale_factor)

    return templates.TemplateResponse("extract_info.html", {"request": request,
                                                            "imagePath": 'public/img/resized_img.jpg',
                                                            "jsonData": result})


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
        data_dict = scale_box(data_dict, 1/scale_factor)
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

        data_dict = format_data_dict(data_dict)
        with open(f"config/template_form/{table_name}.json", 'w', encoding='utf-8') as outfile:
            json.dump(data_dict, outfile, ensure_ascii=False)

        return {"message": f"Table '{table_name}' created successfully."}
    except Exception as e:
        return {"message": f"Error creating table: {str(e)}."}


# FastAPI endpoint to insert data into MySQL table
@app.post("/insert_data")
async def insert_data(data: JSONData):
    try:
        data_dict = json.loads(data.data)
        data_dict = scale_box(data_dict, 1/scale_factor)

        # Filter JSON data for items where class is "text"
        text_columns = [item['text'] for item in data_dict if (item['class'] == 'question' or item['class'] == 'date')]
        text_values = [item['ocr_text'] for item in data_dict if (item['class'] == 'question' or item['class'] == 'date')]
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

    
# Define the path to the mapping.json file
json_file_path = "config/mapping.json"
# Fast api endpoint to retrieve mapping.json and return the json object using get
@app.get("/get-mapping", response_class=JSONResponse)
async def get_mapping():
    try:
        # Open and read the JSON file
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON file")

# Endpoint to retrieve a list of available tables
@app.get("/tables")
async def get_available_tables():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        # Implement logic to retrieve a list of table names from the database
        # You can use information_schema.tables or similar approach
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s", (db_config['database'],))
        table_names = [row[0] for row in cursor.fetchall()]
        cursor.close()
        db.close()
        return table_names
    except Exception as e:
        print(f"Error retrieving table names: {str(e)}")
        return {"message": "Error retrieving table names."}

# Endpoint to retrieve all data from a specific table
@app.get("/showingData/{table_name}")
async def get_table_data(table_name: str):
    if not check_table_exists(table_name):
        return {"message": f"Table '{table_name}' does not exist."}
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        # Get column names
        cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s", (db_config['database'], table_name))
        column_names = [row[0] for row in cursor.fetchall()]

        # Get table data
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return {"column_names": column_names, "inside_data": data}  # Return both column names and data
    except Exception as e:
        print(f"Error retrieving data: {str(e)}")
        return {"message": "Error retrieving data."}


@app.get("/showingData/{table_name}/search")
async def search_table_data(table_name: str, search_term: str = None):
    if not check_table_exists(table_name):
        return {"message": f"Table '{table_name}' does not exist."}
    if not search_term:
        return {"message": "Please provide a search term."}
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        # Get column names
        cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s", (db_config['database'], table_name))
        column_names = [row[0] for row in cursor.fetchall()]

        # Modify this query to filter data based on your search criteria
        cursor.execute(f"SELECT * FROM {table_name} WHERE mssv LIKE %s", (f"%{search_term}%",))
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return {"column_names": column_names, "inside_data": data}  # Return both column names and data
    except Exception as e:
        print(f"Error retrieving data: {str(e)}")
        return {"message": "Error retrieving data."}


@app.post("/showingData/scan")
async def create_table_proceed(request: Request):
    global scale_factor
    try:
        result = subprocess.run(["sh", "./src/BRS/runScanner.sh"], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except Exception as e:
        return {"message": f"Error running command: {str(e)}."}
    
    image = cv2.imread("data/scanned_data/doc_1.png")
    image = imutils.resize(image, width=2000)
    cv2.imwrite(f'data/scanned_data/doc_1.png', image)

    result, status_code, [aligned] = info_extracter.extract_info(image, is_visualize=False)

    cv2.imwrite(f'src/WEB/public/img/temp_img.jpg', aligned)
    # save the resized image
    scale_factor = 1000 / aligned.shape[1]
    resized_img = imutils.resize(aligned, width=1000)
    cv2.imwrite(f'src/WEB/public/img/resized_img.jpg', resized_img)
    # apply scale factor for display on the web
    result = scale_box(result, scale_factor)
    
    return templates.TemplateResponse("extract_info.html", {"request": request,
                                                            "imagePath": 'public/img/resized_img.jpg',
                                                            "jsonData": result})


# Run the application (optional, for development purposes)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
