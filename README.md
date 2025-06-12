# 🧠 themeBot – Document Theme Identifier

A FastAPI + Streamlit powered tool that:
- Accepts PDF uploads (multiple, scanned too!)
- Extracts key text with OCR fallback
- Lets users ask questions per doc
- Returns answers with clear citations (doc, page, para)
- Synthesizes themes (no GPT dependency)

---

## 🚀 Features

- 🔍 Multi-PDF question search
- 🧾 OCR for scanned documents
- 📊 Table-style results with citations
- 📚 Theme summaries per query
- 🧠 Search history retained in session

---

## 📦 Folder Structure

├── backend/ # FastAPI backend logic
├── frontend/ # Streamlit UI
├── docs/ # Documentation + screenshots
├── tests/ # Pytest unit tests
├── demo/ # Sample PDFs to try
└── README.md
---

## 🧪 Quickstart

1. Clone the repo
2. Run:
   ```bash
   pip install -r requirements.txt
   uvicorn backend.app.main:app --reload
   streamlit run frontend/app.py
