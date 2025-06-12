import streamlit as st
import requests
import pandas as pd

# dark mode overrides — no eyeball pain please
st.set_page_config(page_title="themeBot", page_icon="🧠", layout="centered")
st.markdown("""
<style>
body { background: #000 !important; color: #ddd !important; }
.css-18e3th9, .css-1d391kg { background: #121212 !important; }
.stButton>button {
    background-color: #5c27fe;
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
.stButton>button:hover {
    background-color: #3b1cc1;
}
</style>
""", unsafe_allow_html=True)

# your live backend
API_URL = "https://wasserstoff-aiinterntask-3.onrender.com"

# initialize history once
if "history" not in st.session_state:
    st.session_state.history = []

st.title("📄 themeBot vOCR")
st.caption("Upload some PDFs, ask questions, get citations. OCR included.")

pdfs = st.file_uploader("Drop PDF(s) here", type=["pdf"], accept_multiple_files=True)
question = st.text_input("Ask anything", placeholder="e.g. what sections were violated?")

# ---- Upload and Preview ----
if pdfs:
    with st.spinner("Uploading and extracting..."):
        for pdf in pdfs:
            try:
                file_bytes = pdf.getvalue()
                files = {"file": (pdf.name, file_bytes, "application/pdf")}
                res = requests.post(f"{API_URL}/upload/", files=files)

                if res.status_code == 200:
                    data = res.json()
                    st.success(f"✅ {data['filename']} uploaded ({data.get('total_pages', '?')} pages)")
                    st.markdown("#### Sample Preview:")
                    for page in data.get("sample", [])[:2]:
                        st.markdown(f"**Page {page['page']}**")
                        st.code(page["text"][:600])
                else:
                    st.error(f"{pdf.name} upload failed ({res.status_code})")
            except Exception as e:
                st.error(f"Error uploading {pdf.name}: {e}")

    st.markdown("---")

    # ---- Search Logic ----
    if question:
        with st.spinner("Searching for answers..."):
            try:
                files_payload = [
                    ("files", (pdf.name, pdf.getvalue(), "application/pdf")) for pdf in pdfs
                ]
                form_data = {"question": question}

                res = requests.post(f"{API_URL}/chat-summary/", files=files_payload, data=form_data)

                if res.status_code == 200:
                    out = res.json()
                    rows = []

                    for row in out.get("table_data", []):
                        answer_clean = row["answer"].replace("[OCR]", "").strip()
                        ocr_flag = "(OCR)" if "[OCR]" in row["answer"] else ""
                        rows.append({
                            "Document ID": row["doc_id"],
                            "Extracted Answer": answer_clean,
                            "Citation": f"{row['citation']} {ocr_flag}"
                        })

                    if rows:
                        st.markdown("### 📊 Search Results Table")
                        df = pd.DataFrame(rows)
                        st.table(df)

                        # add to session history
                        st.session_state.history.append({
                            "question": question,
                            "table": df
                        })
                    else:
                        st.info("No results found in the documents.")

                else:
                    st.error("Search failed. Try again?")
            except Exception as err:
                st.error(f"Something broke: {err}")

    st.markdown("---")

    # ---- Page-by-page summary for 1st file ----
    st.markdown("## 📂 TL;DR per page (1st file only)")
    try:
        payload = {"file": (pdfs[0].name, pdfs[0].getvalue(), "application/pdf")}
        r = requests.post(f"{API_URL}/classify-pages/", files=payload)

        if r.status_code == 200:
            results = r.json().get("page_summaries", [])
            for entry in results:
                st.markdown(f"**Page {entry['page']}**")
                st.write(entry["summary"])
        else:
            st.warning("Page summarizer didn’t return anything useful.")
    except Exception as e:
        st.error(f"Page classifier error: {e}")

    st.markdown("---")

    # ---- Search History ----
    if st.session_state.history:
        st.markdown("## 🕓 Previous Queries")
        for idx, past in enumerate(reversed(st.session_state.history)):
            st.markdown(f"### 🔁 Query {len(st.session_state.history) - idx}: *{past['question']}*")
            st.table(past["table"])

else:
    st.info("Upload at least one PDF to start.")
