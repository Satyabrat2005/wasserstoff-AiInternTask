from fastapi import APIRouter, UploadFile, File, Form
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
        "sample": pagez[:15]  # lazy preview, 15 is fine
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
async def not_really_chatgpt(file: UploadFile = File(...), question: str = Form(...) ):
    try:
        print(f"got a question: {question}")
        saved = await save_uploaded_file(file, file.filename)
        pages = extract_text_from_pdf(saved)

        # do your theme-style summary thing here
        summary_data = generate_chat_style_summary(pages)

        # Include the user's question in the response for now
        summary_data["chat_summary"] = f"you asked: '{question}'\n\n" + summary_data.get("chat_summary", "")

        return summary_data

    except Exception as e:
        print("chat-summary blew up 💣:", e)
        return {"status": "fail", "error": str(e)}
# this is just a placeholder for the chat summary endpoint