from fastapi import APIRouter, UploadFile, File
from app.services.document_processor import save_uploaded_file, extract_text_from_pdf
from app.services.theme_analyzer import analyze_themes

router = APIRouter()

@router.get("/")
def just_checking():
    return {"msg": "Yo! It's working, GenAI chatbot route up"}

@router.post("/upload/")
async def upload_file_here(file: UploadFile = File(...)):
    # read file into bytes
    stuff = await file.read()

    # save file somewhere
    try:
        file_path = save_uploaded_file(stuff, file.filename)
    except Exception as e:
        return {"error": f"couldn't save file: {e}"}

    # extract text
    try:
        final_text = extract_text_from_pdf(file_path)
    except Exception as e:
        return {"error": f"couldn't extract: {e}"}

    # return sample
    return {
        "filename": file.filename,
        "how_many_pages": len(final_text),
        "sample_pages": final_text[:2]  # just give first two
    }

@router.post("/get-themes/")
async def do_some_theme_analysis(file: UploadFile = File(...)):
    raw = await file.read()

    try:
        pth = save_uploaded_file(raw, file.filename)
        text_data = extract_text_from_pdf(pth)
        result = analyze_themes(text_data)
        return result
    except Exception as err:
        return {"status": "fail", "reason": str(err)}

@router.post("/classify-pages/")
async def classify_each_page(file: UploadFile = File(...)):
    pdf_path = await save_uploaded_file(file)
    pages_data = extract_text_from_pdf(pdf_path)
    page_summaries = []

    for p in pages_data:
        summary = f"Probably something about: {p['text'][:150]}"  # Or call LLM
        page_summaries.append({
            "page": p['page'],
            "summary": summary
        })

    return {"page_summaries": page_summaries}