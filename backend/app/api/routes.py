from fastapi import APIRouter, UploadFile, File
from app.services.document_processor import save_uploaded_file, extract_text_from_pdf
from app.services.theme_analyzer import analyze_themes

router = APIRouter()


@router.get("/")
def ping():
    # it's alive!!! (probably)
    return {"msg": "yep, the backend breathes 😮‍💨"}


# someone pls refactor this later
@router.post("/upload/")
async def badly_named_upload_thing(file: UploadFile = File(...)):
    try:
        print("about to save the file... hope it doesn’t explode")
        saved_path = await save_uploaded_file(file, file.filename)
        pagez = extract_text_from_pdf(saved_path)
        print("ok extracted stuff, probs worked??")
    except Exception as err:
        print("something died 💀:", err)
        return {"error": f"nope. couldn’t read the file: {err}"}

    return {
        "filename": file.filename,
        "total_pages": len(pagez),
        "sample": pagez[:2]  # lazy preview, 2 is fine
    }


@router.post("/get-themes/")
async def themes_idk(file: UploadFile = File(...)):
    try:
        temp = await save_uploaded_file(file, file.filename)
        pages = extract_text_from_pdf(temp)
        # this better return themes or I cry
        theme_stuff = analyze_themes(pages)
        return theme_stuff
    except Exception as e:
        print("theme error:", e)
        return {"status": "fail", "reason": str(e)}


@router.post("/classify-pages/")
async def classify_pages_bro(file: UploadFile = File(...)):
    try:
        path = await save_uploaded_file(file, file.filename)
        pgz = extract_text_from_pdf(path)

        results = []
        for i in pgz:
            txt = i.get("text", "uh nothing here")
            summaryish = f"idk probably about: {txt[:177]}..."
            results.append({
                "page": i.get("page", "???"),
                "summary": summaryish
            })
        return {"page_summaries": results}
    except Exception as e:
        print("classifier borked:", e)
        return {"status": "error", "message": str(e)}


# lol chat summary but not really
@router.post("/chat-summary/")
async def not_really_chatgpt(file: UploadFile = File(...)):
    try:
        meh = await save_uploaded_file(file, file.filename)
        pages = extract_text_from_pdf(meh)
        joined = "\n\n".join([p['text'] for p in pages])
        fake_summary = "ummm... probably this is about: " + joined[:333] + "..."
        some_sources = [f"page {p['page']}" for p in pages[:min(3, len(pages))]]
        return {
            "chat_summary": fake_summary,
            "citations": some_sources
        }
    except Exception as e:
        print("bruh", e)
        return {"status": "fail", "error": str(e)}
# this is just a placeholder for the chat summary endpoint