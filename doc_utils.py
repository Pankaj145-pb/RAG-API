from typing import  List, Tuple

from gemini_client import client

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
