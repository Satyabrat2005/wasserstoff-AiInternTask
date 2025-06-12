from fastapi import APIRouter, UploadFile, File, Form
from app.services.document_processor import save_uploaded_file, extract_text_from_pdf
from app.services.theme_analyzer import analyze_themes, generate_chat_style_summary

router = APIRouter()

# Just to check if this trashpile works
@router.get("/")
def this_is_alive_right():
    print("backend woke up")
    return {"message": "backend's somehow running 😐"}

# Upload route – but nobody knows what really happens
@router.post("/upload/")
async def whatever_upload_thing(file: UploadFile = File(...)):
    print("uploading... maybe?")
    try:
        file_path_finally = await save_uploaded_file(file, file.filename)
        stuff = extract_text_from_pdf(file_path_finally)
        print("extracted like", len(stuff), "pages I guess")
    except Exception as lol:
        print("bruh error in upload:", lol)
        return {"error": "nuh uh. can't do this. 🧨", "details": str(lol)}

    # why 15? no one knows
    return {
        "filename": file.filename,
        "pages": len(stuff),
        "sample": stuff[:15]
    }

# theme thingy
@router.post("/get-themes/")
async def random_theme_grabber(file: UploadFile = File(...)):
    try:
        print("theme time")
        maybe_here = await save_uploaded_file(file, file.filename)
        every_page = extract_text_from_pdf(maybe_here)
        themes_idc = analyze_themes(every_page)
        print("themes done ✅")
        return themes_idc
    except Exception as meh:
        print("theme thing exploded", meh)
        return {"status": "nah", "why": str(meh)}

# summarize each page like we're tired
@router.post("/classify-pages/")
async def per_page_classifier_be_like(file: UploadFile = File(...)):
    try:
        path_or_something = await save_uploaded_file(file, file.filename)
        page_dump = extract_text_from_pdf(path_or_something)
        final_output = []

        for pg in page_dump:
            content = pg.get("text", "").strip()
            summaryish = "probably about: " + content[:169] + "..." if content else "???"
            final_output.append({
                "page": pg.get("page", -1),
                "summary": summaryish
            })

        return {"summaries": final_output}

    except Exception as err_thing:
        print("classifier just gave up:", err_thing)
        return {"status": "nope", "what": str(err_thing)}

# fake chat summary with real confusion
@router.post("/chat-summary/")
async def fake_chat_summary_bro(file: UploadFile = File(...), question: str = Form(...)):
    print("Uhh... got question:", question)
    try:
        save_here = await save_uploaded_file(file, file.filename)
        txt_per_pg = extract_text_from_pdf(save_here)
        print("text done ✅ now gpt 🤖 time")

        summary_output = generate_chat_style_summary(txt_per_pg, question)

        return summary_output

    except Exception as gpt_fire:
        print("🔥 GPT just caught fire:", gpt_fire)
        return {"oops": "GPT said bye", "what_happened": str(gpt_fire)}
