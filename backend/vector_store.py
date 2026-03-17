import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"


def require_openai_api_key() -> None:
    """Validate OpenAI API key presence before embedding/LLM calls."""
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. In PowerShell run: "
            "$env:OPENAI_API_KEY=\"your_api_key\""
        )


def get_embeddings_model() -> OpenAIEmbeddings:
    """Create and return the embeddings model used by the vector store."""
    require_openai_api_key()
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=embedding_model)


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