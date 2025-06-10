import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm

# set uplod dir
UPLOAD_DIR = "backend/data"  # NOTE: maybe change later?

def save_uploaded_file(file_bytes, file_name):  # yes, bytes
    # make sure dir exists
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    f_path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(f_path, "wb") as tempf:
        tempf.write(file_bytes)
    return f_path


def extract_text_from_pdf(pdf_path):
    results = []

    # open the pdf file with fitz (was pymupdf?)
    try:
        doc = fitz.open(pdf_path)
    except Exception as oops:
        print("error opening:", oops)
        return []

    # loop through pages
    for i in tqdm(range(len(doc)), desc="Scraping Pages"):
        pg = doc.load_page(i)  # get page
        try:
            txt = pg.get_text()
        except:
            txt = ""
        
        if txt and len(txt.strip()) > 5:
            results.append({
                "page": i+1,  # human-readable page numbers start at 1
                "text": txt
            })
        else:
            # OCR fallback
            print(f"[INFO] Doing OCR for page {i+1}")
            try:
                imgz = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
                for im in imgz:
                    ocr_result = pytesseract.image_to_string(im)
                    if ocr_result and len(ocr_result.strip()) > 3:
                        results.append({
                            "page": i+1,
                            "text": ocr_result
                        })
            except Exception as er:
                print("OCR fail page", i+1, er)
    
    return results
