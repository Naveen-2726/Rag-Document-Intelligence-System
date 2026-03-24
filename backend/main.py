import os
import time
import shutil
import requests as http_requests
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.file_parser import SUPPORTED_EXTENSIONS, parse_file
from backend.rag_pipeline import ask_question
from backend.text_chunker import split_text
from backend.vector_store import create_vector_store, delete_vector_store

# Load environment variables from .env at startup
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="RAG-Based Universal Document Intelligence System")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:8502",
        "http://127.0.0.1:8502",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check() -> dict:
    """Return API health status."""
    return {"message": "RAG-Based Universal Document Intelligence System is running"}


@app.get("/system/status")
def system_status() -> dict:
    """Return system status information for frontend diagnostics."""
    uploaded_files = [item for item in UPLOAD_DIR.glob("*") if item.is_file()]
    index_exists = (VECTOR_DB_DIR / "index.faiss").exists()

    groq_api_key = os.getenv("GROQ_API_KEY", "")
    groq_api_key_set = bool(groq_api_key and len(groq_api_key) > 10)

    # Quick connectivity check to Groq API
    groq_reachable = False
    if groq_api_key_set:
        try:
            resp = http_requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {groq_api_key}"},
                timeout=5,
            )
            groq_reachable = resp.status_code == 200
        except Exception:
            pass

    # Count total chunks in vector store
    total_chunks = 0
    if index_exists:
        try:
            from backend.vector_store import load_vector_store
            vs = load_vector_store()
            if vs:
                total_chunks = vs.index.ntotal
        except Exception:
            pass

    return {
        "backend": "online",
        "llm_provider": "groq",
        "groq_api_key_set": groq_api_key_set,
        "groq_reachable": groq_reachable,
        "embedding_provider": "huggingface",
        "llm_model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "upload_directory": str(UPLOAD_DIR),
        "uploaded_file_count": len(uploaded_files),
        "vector_index_exists": index_exists,
        "total_chunks": total_chunks,
    }


@app.get("/documents")
def list_documents() -> dict:
    """List uploaded documents currently stored on disk."""
    documents: list[dict] = []
    for file_path in sorted(UPLOAD_DIR.glob("*"), reverse=True):
        if not file_path.is_file():
            continue
        display_name = file_path.name.split("_", maxsplit=1)[1] if "_" in file_path.name else file_path.name
        stat = file_path.stat()
        documents.append(
            {
                "stored_name": file_path.name,
                "name": display_name,
                "size_bytes": stat.st_size,
                "uploaded_at": stat.st_mtime,
            }
        )
    return {"documents": documents, "count": len(documents)}


@app.delete("/documents/{stored_name}")
def delete_document(stored_name: str) -> dict:
    """Delete a specific uploaded document by its stored name."""
    file_path = UPLOAD_DIR / stored_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Document not found")

    file_path.unlink()
    return {"message": f"Deleted {stored_name}", "status": "deleted"}


@app.delete("/documents")
def delete_all_documents() -> dict:
    """Delete all uploaded documents and reset the vector store."""
    # Remove all files in upload dir
    count = 0
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.is_file():
            file_path.unlink()
            count += 1

    # Reset vector store
    delete_vector_store()

    return {"message": f"Deleted {count} document(s) and reset vector store", "deleted_count": count}


@app.post("/upload")
@limiter.limit("10/minute")
async def upload_documents(request: Request, files: list[UploadFile] = File(...)) -> dict:
    """Upload, parse, chunk, and index one or many documents."""
    start_time = time.time()

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    processed_files: list[dict] = []
    total_chunks_added = 0

    for uploaded_file in files:
        extension = Path(uploaded_file.filename or "").suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            processed_files.append(
                {
                    "file": uploaded_file.filename,
                    "status": "failed",
                    "reason": f"Unsupported extension: {extension}",
                }
            )
            continue

        unique_name = f"{uuid4().hex}_{uploaded_file.filename}"
        destination = UPLOAD_DIR / unique_name

        try:
            with open(destination, "wb") as file_handle:
                file_handle.write(await uploaded_file.read())

            extracted_text = parse_file(destination)
            if not extracted_text.strip():
                raise ValueError("No extractable text found in file")

            documents = split_text(extracted_text, source=uploaded_file.filename or unique_name)
            create_vector_store(documents)

            chunk_count = len(documents)
            total_chunks_added += chunk_count
            processed_files.append(
                {
                    "file": uploaded_file.filename,
                    "status": "processed",
                    "chunks": chunk_count,
                }
            )
        except Exception as exc:
            processed_files.append(
                {
                    "file": uploaded_file.filename,
                    "status": "failed",
                    "reason": str(exc),
                }
            )

    elapsed_ms = round((time.time() - start_time) * 1000)

    return {
        "message": "Upload completed",
        "total_files": len(files),
        "total_chunks_added": total_chunks_added,
        "processing_time_ms": elapsed_ms,
        "results": processed_files,
    }


@app.get("/ask")
@limiter.limit("20/minute")
def ask(request: Request, query: str = Query(..., min_length=3), k: int = Query(4, ge=1, le=12)) -> dict:
    """Answer a question using indexed document knowledge and return citations."""
    start_time = time.time()
    try:
        result = ask_question(query=query, k=k)
        elapsed_ms = round((time.time() - start_time) * 1000)
        result["processing_time_ms"] = elapsed_ms
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc