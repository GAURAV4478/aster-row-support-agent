
import os
import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
COLLECTION_NAME = "aster_row_kb"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def reset_collection():
    """Delete and recreate the collection - makes re-ingestion idempotent,
    so running pipeline.py twice never leaves duplicate/stale chunks behind."""
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return client.create_collection(COLLECTION_NAME)


def get_collection():
    client = get_client()
    return client.get_collection(COLLECTION_NAME)


def add_chunks(ids, docs, metadatas, embeddings):
    collection = get_collection()
    collection.add(ids=ids, documents=docs, metadatas=metadatas, embeddings=embeddings)


def query(query_embedding, n_results: int = 5):
    """
    Returns raw Chroma results (documents, metadatas, distances).
    Deliberately does NOT filter by status here - that filtering logic
    belongs in retrieval.py, one layer up, so this file stays a dumb,
    reusable search primitive with no business rules baked in.
    """
    collection = get_collection()
    return collection.query(query_embeddings=[query_embedding], n_results=n_results)