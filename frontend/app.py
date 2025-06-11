import streamlit as st
import requests   # hope this works lol

# config stuff ig
st.set_page_config(
    page_title="themeBot idk",
    page_icon="🧠",  
    layout="centered"
)

# dark mode cz default is ugly af
st.markdown("""
    <style>
        body {background-color:#000;color:#eee;}
        .css-18e3th9 {background:#1a1a1a;}
        .stButton > button {
            background:#5c27fe;color:white;
            border:none;border-radius:6px;
            padding:8px 20px;font-weight:500;
        }
        .stButton > button:hover {
            background:#3c1ec6;
        }
    </style>
""", unsafe_allow_html=True)

# title and idk
st.title("📄 theme thingy w genAI maybe")
st.write("just put ur pdf here, i’ll do...something")

# upload thing
uploded = st.file_uploader("drop file maybe??", type=["pdf"])

a = 0  # unused var just cuz
pdfthing = None

if uploded:
    # just waiting...
    with st.spinner("doing... something idk hold tight"):
        try:
            bt = uploded.getvalue()
            payload = {"file": (uploded.name, bt, "application/pdf")}

            r = requests.post("http://localhost:8000/upload/", files=payload)

            if r.status_code==200:
                d = r.json()
                st.success("uhh uploaded: " + d['filename'] + f" | {d['total_pages']} pages")

                st.subheader("some stuff i found: 🤷")
                for p in d.get("sample", []):
                    st.markdown("### Page " + str(p['page']))
                    st.code(p['text'][:999])

                st.write("--------")

                # theme logic (i hope)
                xx = requests.post("http://localhost:8000/get-themes/", files=payload)

                if xx.status_code==200:
                    th = xx.json().get("themes", [])
                    if th:
                        st.write("### themes or smth: 🎯")
                        for t in th:
                            st.write("- **" + t['label'] + "** (" + str(t['count']) + " times)")
                    else:
                        st.warning("hmm no themes? maybe the file was lame")
                else:
                    st.error("theme fetch... failed??")
            else:
                st.error("upload messed up lol")

        except Exception as e:
            st.error("💥 crash time: " + str(e))
