import os
from pathlib import Path
from functools import lru_cache

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"


@lru_cache(maxsize=1)
def get_embeddings_model() -> HuggingFaceEmbeddings:
    """Create and return a cached singleton HuggingFace embeddings model.

    The model is loaded once and reused across all requests, saving ~2-3s
    per operation that would otherwise be spent on model initialization.
    """
    model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "batch_size": 64},
    )


def load_vector_store() -> FAISS | None:
    """Load persisted FAISS index if it exists, otherwise return None."""
    index_file = VECTOR_DB_DIR / "index.faiss"
    if not index_file.exists():
        return None

    embeddings = get_embeddings_model()
    return FAISS.load_local(
        str(VECTOR_DB_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def create_vector_store(documents: list[Document]) -> FAISS:
    """Insert documents into FAISS index and persist index to disk."""
    if not documents:
        raise ValueError("No documents provided to create_vector_store")

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    embeddings = get_embeddings_model()
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    index_exists = os.path.exists(str(VECTOR_DB_DIR / "index.faiss"))
    if index_exists:
        current_store = FAISS.load_local(
            str(VECTOR_DB_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        current_store.add_texts(texts=texts, metadatas=metadatas)
    else:
        current_store = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
        )

    current_store.save_local(str(VECTOR_DB_DIR))
    return current_store


def delete_vector_store() -> bool:
    """Delete the persisted FAISS index from disk. Returns True if deleted."""
    import shutil
    if VECTOR_DB_DIR.exists():
        shutil.rmtree(VECTOR_DB_DIR)
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        return True
    return False