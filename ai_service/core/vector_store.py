import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")

_embeddings = None
_store = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return _embeddings


def get_vector_store() -> Chroma:
    global _store
    if _store is None:
        _store = Chroma(
            collection_name="jobs",
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_DIR,
        )
    return _store


def index_jobs(jobs: list[dict]):
    """Add job descriptions to the vector store."""
    store = get_vector_store()
    texts = [f"{j['title']} at {j['company']}\n{j['description']}" for j in jobs]
    metadatas = [{k: v for k, v in j.items() if k != 'description'} for j in jobs]
    ids = [str(j['id']) for j in jobs]
    store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    store.persist()
