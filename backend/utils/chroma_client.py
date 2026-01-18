# backend/utils/chroma_client.py
import os
import uuid
from typing import List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions

# ----------------------------------------------------------------------
# Chemin du vecteur‑store (défini via variable d’environnement ou fallback)
# ----------------------------------------------------------------------
CHROMA_DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    os.path.expanduser("~/.chroma")   # même répertoire que précédemment
)

# ----------------------------------------------------------------------
# Client persistant – API moderne (v0.5+)
# ----------------------------------------------------------------------
# Le constructeur accepte simplement le chemin du répertoire.
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# ----------------------------------------------------------------------
# Collection unique « default » – créée à la volée si elle n’existe pas
# ----------------------------------------------------------------------
_COLLECTION_NAME = "default"

def _get_collection():
    """
    Retourne (ou crée) la collection nommée « default ».
    Utilise le même embedding function que précédemment.
    """
    if _COLLECTION_NAME in client.list_collections():
        return client.get_collection(name=_COLLECTION_NAME)

    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2",
        device="cpu",               # on utilise le CPU (ou le GPU via CoreML si disponible)
    )
    return client.create_collection(
        name=_COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"description": "Knowledge base for chloe‑code"},
    )

# ----------------------------------------------------------------------
# 1️⃣  Recherche de documents
# ----------------------------------------------------------------------
def search_kb(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Recherche les `k` documents les plus similaires à `query`.
    Retourne une liste de dicts compatibles avec le schéma SearchResult.
    """
    collection = _get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    items = []
    for doc, meta, dist in zip(docs, metas, distances):
        score = 1.0 - float(dist)          # distance → score (0‑1)
        items.append(
            {
                "title": meta.get("title", "Untitled"),
                "snippet": doc,
                "url": meta.get("url"),
                "score": round(score, 4),
            }
        )
    return items

# ----------------------------------------------------------------------
# 2️⃣  Ajout / indexation de documents
# ----------------------------------------------------------------------
def add_documents(
    documents: List[str],
    metadatas: List[Dict[str, Any]] = None,
) -> None:
    """
    Ajoute une série de blocs de code (documents) dans la collection.
    Si `metadatas` n’est pas fourni, on crée des titres génériques.
    """
    collection = _get_collection()
    if metadatas is None:
        metadatas = [{"title": f"doc-{uuid.uuid4()}"} for _ in documents]

    ids = [str(uuid.uuid4()) for _ in documents]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )