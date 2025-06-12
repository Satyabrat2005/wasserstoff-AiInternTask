# 🧩 FastAPI Endpoint Reference – themeBot Backend

This doc lists and explains all the backend routes exposed by our FastAPI app.

---

## 📡 GET /
### What it does:

Quick sanity check to make sure the backend is up and running.
Doesn’t do anything fancy — just confirms FastAPI is alive.

### How to use :
Open your browser or hit it with curl:

bash : curl http://localhost:8000/

You’ll get something like:

{
  "msg": "yeah... it's alive. somehow."
}