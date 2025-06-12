import os
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm

# just drop everything into this folder (lazy, but works)
UPLOAD_DIR = "backend/data"

def save_uploaded_file(file_bytes, file_name):
    """
    Save the uploaded file to disk.
    Just saves raw bytes into backend/data.
    """
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    path = os.path.join(UPLOAD_DIR, file_name)
    
    with open(path, "wb") as f:
        f.write(file_bytes)
    
    return path

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF.
    - First tries to use PyMuPDF (fitz)
    - If it fails or finds nothing, does OCR with pytesseract
    """
    text_results = []

    try:
        doc = fitz.open(pdf_path)
    except Exception as err:
        print("💥 Couldn't open the PDF:", err)
        return []

    for i in tqdm(range(len(doc)), desc="Scraping Pages"):
        page_num = i + 1
        try:
            page = doc.load_page(i)
            txt = page.get_text()
        except Exception as boom:
            print(f"😵 failed to load page {page_num}:", boom)
            txt = ""

        # if the page had proper text, store that
        if txt and len(txt.strip()) > 5:
            text_results.append({
                "page": page_num,
                "text": txt.strip()
            })
        else:
            # OCR fallback if .get_text() gave up
            print(f"🔍 Page {page_num} is probably scanned. Running OCR...")
            try:
                images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
                for image in images:
                    ocr_text = pytesseract.image_to_string(image)
                    if ocr_text and len(ocr_text.strip()) > 3:
                        text_results.append({
                            "page": page_num,
                            "text": f"[OCR] {ocr_text.strip()}"
                        })
                    else:
                        print(f"😑 OCR found nothing on page {page_num}")
            except Exception as oops:
                print(f"💀 OCR crash on page {page_num}:", oops)
                text_results.append({
                    "page": page_num,
                    "text": "[OCR] Failed to extract text"
                })

    return text_results
