import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

# just putting everything in one place (folder)
CHROMA_PATH = "backend/data/vectorstore"
os.makedirs(CHROMA_PATH, exist_ok=True)

# init embed model
try:
    embedder = OpenAIEmbeddings()
except Exception as e:
    print("Couldn't load OpenAI embeddings:", e)
    embedder = None  # just in case

# init vector store globally so we don't keep loading it
try:
    vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedder)
except Exception as e:
    print("Chroma init failed:", e)
    vectordb = None

def add_texts_to_vectorstore(text_chunks, metadata_chunks=None):
    # feed stuff to vectorstore
    docs = []

    for i, chunk in enumerate(text_chunks):
        meta = {}
        if metadata_chunks and i < len(metadata_chunks):
            meta = metadata_chunks[i]
        docs.append(Document(page_content=chunk, metadata=meta))

    try:
        vectordb.add_documents(docs)
        vectordb.persist()
        return True
    except Exception as err:
        print("Error adding to vectorstore:", err)
        return False

def query_vectorstore(query, top_k=3):
    # basic search
    try:
        res = vectordb.similarity_search(query, k=top_k)
        return [r.page_content for r in res]
    except Exception as er:
        print("Search error:", er)
        return []
