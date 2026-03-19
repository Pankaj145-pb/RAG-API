import glob
import os
from typing import Iterable, List, Tuple

from google import genai
from PyPDF2 import PdfReader
from gemini_client import client

def extract_text_from_path(path: str) -> str:
    """Return extracted text of a supported file (PDF or TXT)."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    raise ValueError(f"Unsupported file type: {ext}")


def load_documents_from_folder(folder: str, extensions: Iterable[str] = (".pdf", ".txt")) -> List[Tuple[str, str]]:
    """Load all documents in a folder and return list of (id, text)."""

    paths: List[str] = []
    for ext in extensions:
        paths.extend(sorted(glob.glob(os.path.join(folder, f"*{ext}"))))

    docs: List[Tuple[str, str]] = []
    for path in paths:
        doc_id = os.path.splitext(os.path.basename(path))[0]
        docs.append((doc_id, extract_text_from_path(path)))

    return docs


def embed_and_add(
    collection,
    docs: List[Tuple[str, str]],
    model: str = "gemini-embedding-001"
) -> None:

    if not docs:
        return

    ids, texts = zip(*docs)
    embeddings = []

    for text in texts:
        result = client.models.embed_content(
            model=model,
            contents=text
        )
        embeddings.append(result.embeddings[0].values)

    collection.add(
        documents=list(texts),
        ids=list(ids),
        embeddings=embeddings
    )
