from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Annotated, List
import os
import uuid
import chromadb
from google import genai
from dotenv import load_dotenv
from doc_utils import embed_and_add
from gemini_client import client
from fastapi.openapi.utils import get_openapi

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment variables")

DOCS_DIR = "documents"
os.makedirs(DOCS_DIR, exist_ok=True)

app = FastAPI()

# ── fix for Swagger UI file picker bug in FastAPI >= 0.129.1 ─────────────────
def _fix_file_upload_schemas(schema: dict) -> None:
    for component in schema.get("components", {}).get("schemas", {}).values():
        for prop in component.get("properties", {}).values():
            if prop.get("contentMediaType") == "application/octet-stream":
                del prop["contentMediaType"]
                prop["format"] = "binary"
            items = prop.get("items", {})
            if items.get("contentMediaType") == "application/octet-stream":
                del items["contentMediaType"]
                items["format"] = "binary"

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    _fix_file_upload_schemas(schema)
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")


# ── helper ──────────────────────────────────────────────────────────────────
def get_embedding(text: str) -> list[float]:
    """Get embedding using the new Gemini SDK client."""
    # FIX 2: Use client.models.embed_content (new SDK syntax)
    result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text
)
    return result.embeddings[0].values        # new SDK returns object, not dict


# ── routes ───────────────────────────────────────────────────────────────────
@app.post("/query")
def query(q: str):
    try:
        # Embed the query
        q_emb = get_embedding(q)

        results = collection.query(query_embeddings=[q_emb], n_results=3)
        context = "\n".join(results["documents"][0]) if results["documents"] else ""

        prompt = f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:"

        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = resp.text

        return {
            "status": "success",
            "question": q,
            "answer": answer,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/reset")
def reset_collection():
    global collection
    chroma.delete_collection("docs")
    collection = chroma.get_or_create_collection("docs")
    return {"status": "success", "message": "Collection reset — ready for new embeddings"}


@app.post("/add")
def add_knowledge(text: str):
    try:
        docs = [(str(uuid.uuid4()), text)]
        embed_and_add(collection, docs)

        return {
            "status": "success",
            "message": "Content added to knowledge base",
            "id": docs[0][0],
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/addFiles")
async def add_files(
    files: Annotated[
        List[UploadFile],
        File(description="Select PDF or TXT files to upload")
    ]
):
    try:
        from pypdf import PdfReader

        stored_texts = []
        doc_ids = []

        for upload in files:
            filename = os.path.basename(upload.filename)
            dest_path = os.path.join(DOCS_DIR, filename)

            content = await upload.read()
            with open(dest_path, "wb") as f:
                f.write(content)

            ext = os.path.splitext(filename)[1].lower()
            if ext == ".pdf":
                reader = PdfReader(dest_path)
                pages = [p.extract_text() or "" for p in reader.pages]
                stored_texts.append("\n".join(pages))
            else:
                stored_texts.append(content.decode("utf-8", errors="replace"))

            doc_ids.append(str(uuid.uuid4()))

        embeddings = [get_embedding(text) for text in stored_texts]

        collection.add(
            documents=stored_texts,
            ids=doc_ids,
            embeddings=embeddings
        )

        return {
            "status": "success",
            "message": f"{len(files)} file(s) added to knowledge base",
            "ids": doc_ids,
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )