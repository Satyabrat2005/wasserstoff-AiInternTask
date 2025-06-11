from fastapi import FastAPI, UploadFile, File
from app.services.document_processor import save_uploaded_file, extract_text_from_pdf
from app.api.routes import router as api_router

app = FastAPI()

@app.get("/")
def home():
    return {"message": "GenAI Document Chatbot - Basic API Running"}

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    saved_path = save_uploaded_file(contents, file.filename)
    extracted_text = extract_text_from_pdf(saved_path)

    try:
        extracted_text = extract_text_from_pdf(saved_path)
    except Exception as e:
        return {"error": f"Failed to process PDF: {str(e)}"}

    return {
        "filename": file.filename,
        "total_pages": len(extracted_text),
        "sample": extracted_text[:2]  # return first 2 pages
    }
#  Include the router from routes.py
app.include_router(api_router)
