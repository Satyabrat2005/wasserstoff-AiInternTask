import streamlit as st
import requests

# IDK what goes here, just some boring setup
st.set_page_config(page_title="themeBot idk", page_icon="🧠", layout="centered")

# throw some css dark sauce
st.markdown("""
<style>
body { background: #000 !important; color: #ddd !important; }
.css-18e3th9, .css-1d391kg { background: #121212 !important; }
.stButton>button {
    background-color: #5c27fe;
    color: #fff;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #3b1cc1;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 themeBot v??")
st.caption("drop pdf → magic happens → hopefully")

pdf = st.file_uploader("yeet ur PDF here 👇", type=["pdf"])
question = st.text_input("ask anything dumb or deep:", placeholder="e.g. what’s this even about?")

if pdf:
    file_bytes = pdf.getvalue()
    actual_payload = {"file": (pdf.name, file_bytes, "application/pdf")}

    with st.spinner("doing techy stuff... 🤓"):
        try:
            resp = requests.post("http://localhost:8000/upload/", files=actual_payload)
            if resp.status_code == 200:
                out = resp.json()
                st.success(f"✅ uploaded {out['filename']} with {out['total_pages']} pages lol")
                st.subheader("👀 sample stuff inside:")
                for pg in out.get("sample", []):
                    st.markdown(f"**Page {pg['page']}**")
                    st.code(pg["text"][:777])  # 777 bc why not
            else:
                st.error("bruh the upload didn’t go through")

        except Exception as oops:
            st.error("💥 something exploded: " + str(oops))

    st.markdown("---")

    # THEME THING
    with st.spinner("digging for themes or whatever..."):
        try:
            t = requests.post("http://localhost:8000/get-themes/", files=actual_payload)
            if t.status_code == 200:
                themez = t.json().get("themes", [])
                if themez:
                    st.markdown("## 🎯 vibes we picked up:")
                    for theme in themez:
                        st.markdown(f"- **{theme['label']}** — mentioned `{theme['count']} times`")
                else:
                    st.warning("bro this pdf has no flavor 😶")
            else:
                st.error("theme engine said no")
        except Exception as eh:
            st.error("theme extraction died 💀: " + str(eh))

    st.markdown("---")

    # if user typed something
    if question:
        with st.spinner("asking the sacred pdf spirit..."):
            try:
                chat = requests.post(
                 "http://localhost:8000/chat-summary/",
                 files=actual_payload,
                data={"question": question}  # <- THIS IS MANDATORY
                )
                if chat.status_code == 200:
                    chatdata = chat.json()
                    st.markdown("### 🧠 what it kinda says:")
                    st.write(chatdata.get("chat_summary", "brain empty ngl"))

                    st.markdown("#### 🧾 some receipts (quotes)")
                    for q in chatdata.get("citations", []):
                        st.markdown(f"- {q}")
                else:
                    st.warning("no answer... maybe pdf ghost took a nap")
            except Exception as yikes:
                st.error("📉 failed to think: " + str(yikes))

    st.markdown("---")

    # PER PAGE STUFF
    st.markdown("## 🗂️ page-by-page tea (⚠️ tl;dr inside)")
    try:
        paged = requests.post("http://localhost:8000/classify-pages/", files=actual_payload)
        if paged.status_code == 200:
            allz = paged.json().get("page_summaries", [])
            for one in allz:
                st.markdown(f"### 📄 Page {one['page']}")
                st.write(one["summary"])
        else:
            st.warning("page stuff went sleepy")
    except Exception as panic:
        st.error("💣 the breakdown broke down: " + str(panic))

else:
    st.warning("👋 hey, you gotta upload *something* first bro")
