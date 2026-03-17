import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.file_parser import SUPPORTED_EXTENSIONS, parse_file
from backend.rag_pipeline import ask_question
from backend.text_chunker import split_text
from backend.vector_store import create_vector_store

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="RAG-Based Universal Document Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    key_configured = bool(os.getenv("OPENAI_API_KEY"))

    return {
        "backend": "online",
        "openai_key_configured": key_configured,
        "upload_directory": str(UPLOAD_DIR),
        "uploaded_file_count": len(uploaded_files),
        "vector_index_exists": index_exists,
    }


@app.get("/documents")
def list_documents() -> dict:
    """List uploaded documents currently stored on disk."""
    documents: list[dict] = []
    for file_path in sorted(UPLOAD_DIR.glob("*"), reverse=True):
        if not file_path.is_file():
            continue
        display_name = file_path.name.split("_", maxsplit=1)[1] if "_" in file_path.name else file_path.name
        documents.append(
            {
                "stored_name": file_path.name,
                "name": display_name,
                "size_bytes": file_path.stat().st_size,
            }
        )
    return {"documents": documents, "count": len(documents)}


@app.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)) -> dict:
    """Upload, parse, chunk, and index one or many documents."""
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

    return {
        "message": "Upload completed",
        "total_files": len(files),
        "total_chunks_added": total_chunks_added,
        "results": processed_files,
    }


@app.get("/ask")
def ask(query: str = Query(..., min_length=3), k: int = Query(4, ge=1, le=12)) -> dict:
    """Answer a question using indexed document knowledge and return citations."""
    try:
        return ask_question(query=query, k=k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc