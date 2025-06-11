import os
from dotenv import load_dotenv

# if user wants to use a .env file, load it
load_dotenv()

# db stuff 
# TODO: remove if unused later
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./dummy.db")

# used for storing pdf uploads and stuff
UPLOADS_PATH = os.getenv("UPLOADS_DIR", "backend/data")

# vector db path, but not sure if this is final
VECTOR_STORE_PATH = os.getenv("VECTOR_DIR", "backend/data/vectorstore")

# not sure if this is useful anymore
DEBUG_MODE = os.getenv("DEBUG", "true").lower() == "true"

# print config for debugging
print("CONFIG LOADED:")
print("UPLOADS_PATH ->", UPLOADS_PATH)
print("VECTOR_STORE_PATH ->", VECTOR_STORE_PATH)
print("DEBUG_MODE ->", DEBUG_MODE)
