from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import easyocr
import numpy as np
from io import BytesIO
from PIL import Image
import re
from fastapi.responses import JSONResponse
import base64

app = FastAPI()

origins = [
    "http://localhost:3000",  # Add your frontend URL here or use it if you are testing locally make sure to change the port number
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = easyocr.Reader(['en'], gpu=False)

def perform_ocr(image_bytes):
    image = np.array(Image.open(BytesIO(image_bytes)))
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

    ocr_output = reader.readtext(thresh_image)
    return image, ocr_output

def extract_useful_information(recognized_text):
    manufacturing_date = None
    expiry_date = None
    company_name = None
    text_string = " ".join(recognized_text)

    mfg_pattern = r'(Mfg Date|Manufactured On|Manufacture Date|Packed On|Pack Date|Made On|Date of Manufacture)\s*([0-9]{1,2}\s*[A-Z]{3}\s*[0-9]{4}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})'
    exp_pattern = r'(Exp Date|Expiry Date|Expired On|Best Before|Best Before Use|Use By)\s*([0-9]{1,2}\s*[A-Z]{3}\s*[0-9]{4}|[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}|[0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4}|([0-9]+)\s*Days|([0-9]+)\s*Year)'
    company_pattern = r'(Mktd by|Pkd by|Manufactured by|Marketing By)\s*([A-Za-z0-9\s&,.]+)'

    mfg_match = re.search(mfg_pattern, text_string, re.IGNORECASE)
    if mfg_match:
        manufacturing_date = mfg_match.group(2)

    exp_match = re.search(exp_pattern, text_string, re.IGNORECASE)
    if exp_match:
        expiry_date = exp_match.group(2)

    company_match = re.search(company_pattern, text_string, re.IGNORECASE)
    if company_match:
        company_name = company_match.group(2).strip()

    return company_name, manufacturing_date, expiry_date

def convert_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def draw_ocr_results(image, ocr_output):
    for (bbox, text, prob) in ocr_output:
        (top_left, top_right, bottom_right, bottom_left) = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))

        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(image, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return image

@app.post("/extract/")
async def extract_info(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    if not image_bytes:
        return JSONResponse(content={"error": "No image provided"}, status_code=400)

    image = Image.open(BytesIO(image_bytes))
    jpeg_bytes = BytesIO()
    image.convert("RGB").save(jpeg_bytes, format="JPEG")
    jpeg_bytes.seek(0)

    image, ocr_output = perform_ocr(jpeg_bytes.getvalue())
    
    image_with_results = draw_ocr_results(image, ocr_output)

    img_base64 = convert_image_to_base64(image_with_results)

    recognized_text = [text for _, text, _ in ocr_output]
    company_name, manufacturing_date, expiry_date = extract_useful_information(recognized_text)

    return JSONResponse(content={
        "company_name": company_name,
        "manufacturing_date": manufacturing_date,
        "expiry_date": expiry_date,
        "ocr_output_image": img_base64, 
        "recognized_text": recognized_text 
    })
