import streamlit as st
import requests

# basic setup
st.set_page_config(page_title="themeBot", page_icon="🧠", layout="centered")

# dark theme override (couldn’t stand the default white)
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

st.title("📄 themeBot vOCR")
st.caption("Upload PDF files. Ask stuff. Get answers. OCR if needed.")

# multiple PDF upload
pdfs = st.file_uploader("Drop PDF(s) here", type=["pdf"], accept_multiple_files=True)
question = st.text_input("Ask anything", placeholder="e.g. what fines were issued?")

# only continue if we have files
if pdfs:
    with st.spinner("Uploading and parsing..."):
        for pdf in pdfs:
            try:
                file_bytes = pdf.getvalue()
                files = {"file": (pdf.name, file_bytes, "application/pdf")}
                r = requests.post("http://localhost:8000/upload/", files=files)

                if r.status_code == 200:
                    data = r.json()
                    st.success(f"{data['filename']} uploaded ({data.get('total_pages', '?')} pages)")
                    st.markdown("#### Sample Preview")
                    for page in data.get("sample", [])[:2]:
                        st.markdown(f"**Page {page['page']}**")
                        st.code(page["text"][:600])
                else:
                    st.error(f"{pdf.name} upload failed (status {r.status_code})")
            except Exception as e:
                st.error(f"{pdf.name} upload crashed: {e}")

    st.markdown("---")

    # process question if given
    if question:
        with st.spinner("Looking through all docs..."):
            try:
                files_payload = [
                    ("files", (pdf.name, pdf.getvalue(), "application/pdf")) for pdf in pdfs
                ]
                form_payload = {"question": question}

                res = requests.post("http://localhost:8000/chat-summary/", files=files_payload, data=form_payload)

                if res.status_code == 200:
                    output = res.json()
                    st.markdown("### 📌 Search Results")

                    for row in output.get("table_data", []):
                        doc = row['doc_id']
                        citation = row['citation']
                        is_ocr = "[OCR]" in row["answer"]
                        answer = row["answer"].replace("[OCR]", "").strip()

                        st.markdown(f"""
**📄 File:** `{doc}`  
📍 **Location:** {citation} {"🧾 OCR" if is_ocr else ""}  
💬 **Text:**  
> {answer}
""")
                else:
                    st.error("Search request failed")
            except Exception as e:
                st.error(f"Search crashed: {e}")

    st.markdown("---")

    # quick summary per page — only first PDF
    if pdfs:
        st.markdown("### 📂 TL;DR for first doc (page-wise)")

        try:
            payload = {"file": (pdfs[0].name, pdfs[0].getvalue(), "application/pdf")}
            r = requests.post("http://localhost:8000/classify-pages/", files=payload)

            if r.status_code == 200:
                results = r.json().get("page_summaries", [])
                for entry in results:
                    st.markdown(f"**Page {entry['page']}**")
                    st.write(entry["summary"])
            else:
                st.warning("Page summary didn't return anything useful.")
        except Exception as e:
            st.error(f"Page breakdown exploded: {e}")
else:
    st.info("Upload at least one PDF to get started.")
