import os

import chromadb
import google.generativeai as genai

from doc_utils import embed_and_add, load_documents_from_folder

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable")
genai.configure(api_key=GEMINI_API_KEY)

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection("docs")

# Load and embed all supported documents from the documents folder
DOCS_DIR = "documents"

docs = load_documents_from_folder(DOCS_DIR)
if not docs:
    raise FileNotFoundError(f"No supported documents found in '{DOCS_DIR}'")

embed_and_add(collection, docs)

print(f"Stored embeddings for {len(docs)} file(s) in Chroma from '{DOCS_DIR}'")
