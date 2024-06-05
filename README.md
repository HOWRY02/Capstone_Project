# Capstone project
## DESCRIPTION
The Prescription Parser project: A program that reads information of Prescription form Image


## REQUIREMENTS (TESTED)
- Ubuntu 20.04 LTS
- Python 3.8.15
- FastAPI 
## Code structure
bash
├── config
├── data
├── model
│   ├── detection_model
│   ├── doc_model
│   └── recognition_model
├── src
│   ├── DOC_AI
│   │   ├── form_understanding
│   │   │   ├── form_understand.py
│   │   └── layout_analysis
│   │       └── layout_analyzer.py
│   ├── OCR
│   │   ├── detection
│   │   │   ├── text_detection.py
│   │   │   └── text_detector.py
│   │   ├── extraction
│   │   │   ├── text_extraction.py
│   │   │   └── text_extractor.py
│   │   ├── recognition
│   │   │   └── text_recognizer.py
│   └── WEB
│   │   ├── public
│   │   └── resources
│   │       ├── script
│   │       └── views
│   ├── utils
│   │   └── utility.py
│   ├── info_extracter.py
│   ├── table_creater.py
│   └── paper_ocr.py
├── evaluate.py
├── main.py
├── README.md
└── requirements.txt
    

## INSTALLATION
- If using GPU, comment line 18 in requirements.txt and uncomment line 21. 
    1. Create virtual environment in anaconda:
        
        conda create --name "name environment" python=3.8
        
    2. Activate environment
        
        conda activate "name environment"
        
    3. Install library:
        
        pip install -r requirements.txt
        

## HOW TO RUN
### Run API server:

uvicorn main:app --host 0.0.0.0 --port 8000
    
## BACKLOG
## FURTHER IMPROVEMENT
## DEPLOYMENT


