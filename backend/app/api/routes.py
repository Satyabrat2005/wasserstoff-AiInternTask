from fastapi import APIRouter, UploadFile, File, Form
from typing import List
from app.services.document_processor import save_uploaded_file, extract_text_from_pdf
from app.services.theme_analyzer import analyze_themes, extract_relevant_answers, generate_chat_style_summary

router = APIRouter()

# is the server breathing? poke it to find out
@router.get("/")
def is_it_working_or_na():
    print("👀 someone pinged us. shocking.")
    return {"msg": "backend’s technically running... somehow 🧟"}


# Upload a PDF and hope everything doesn’t explode
@router.post("/upload/")
async def dump_pdf_here(file: UploadFile = File(...)):
    print(f"received file: {file.filename} – guess I’ll try to handle it 😩")

    try:
        # read the file like it's 2005 and we forgot async existed
        file_bytes = await file.read()
        path = save_uploaded_file(file_bytes, file.filename)
        pages = extract_text_from_pdf(path)
        print(f"extracted like {len(pages)} pages? I hope. 📄")
    except Exception as chaos:
        print("🚨 OH NO: upload crashed hard:", chaos)
        return {
            "error": "nope. couldn’t process that mess 🤷‍♂️",
            "excuse": str(chaos)
        }

    return {
        "filename": file.filename,
        "num_pages": len(pages),
        "sample_pages": pages[:15]  # 15 is not negotiable.
    }


# Try to extract “themes” like we know what we’re doing
@router.post("/get-themes/")
async def kinda_sorta_find_themes(file: UploadFile = File(...)):
    print("⚙️ okay let’s try to find some 'themes' or whatever")

    try:
        file_bytes = await file.read()
        path = save_uploaded_file(file_bytes, file.filename)
        pages = extract_text_from_pdf(path)
        themes = analyze_themes(pages)
        print("✨ found a few things that looked like themes. maybe.")
        return themes
    except Exception as meltdown:
        print("💣 theme analyzer just collapsed:", meltdown)
        return {
            "status": "bruh no",
            "error": str(meltdown)
        }


# Summarize each page. Badly. With vibes.
@router.post("/classify-pages/")
async def really_loose_page_summary(file: UploadFile = File(...)):
    print("📝 about to summarize pages. loosely. very loosely.")

    try:
        file_bytes = await file.read()
        path = save_uploaded_file(file_bytes, file.filename)
        pages = extract_text_from_pdf(path)

        results = []
        for pg in pages:
            text = pg.get("text", "").strip()
            snippet = text[:177] + "..." if text else "🫠 literally nothing here"
            results.append({
                "page": pg.get("page", "no clue"),
                "summary": f"probably about: {snippet}"
            })

        print("📦 page summaries done-ish")
        return {"summaries": results}

    except Exception as this_is_fine:
        print("🔥 classifier faceplanted:", this_is_fine)
        return {
            "status": "nah",
            "what": str(this_is_fine)
        }


# Pretend to be chatGPT without actually being one (we swear)
@router.post("/chat-summary/")
async def search_across_documents(files: List[UploadFile] = File(...), question: str = Form(...)):
    all_results = []

    print(f"🔍 Searching for: {question}")

    try:
        for file in files:
            print(f"📂 Processing: {file.filename}")
            file_bytes = await file.read()
            file_path = save_uploaded_file(file_bytes, file.filename)
            pages = extract_text_from_pdf(file_path)

            matches = extract_relevant_answers(pages, question)

            for match in matches:
                all_results.append({
                    "doc_id": file.filename,
                    "answer": match["answer"],
                    "citation": f"Page {match['page']}, Para {match['paragraph']}"
                })

        return {
            "table_data": all_results,
            "chat_summary": f"Found {len(all_results)} results across {len(files)} document(s)."
        }

    except Exception as kaboom:
        print("🔥 exploded:", kaboom)
        return {"error": str(kaboom)}