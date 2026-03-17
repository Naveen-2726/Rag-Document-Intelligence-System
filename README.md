# RAG-Based Universal Document Intelligence System

An end-to-end AI application for multi-document understanding using FastAPI, Streamlit, LangChain, OpenAI embeddings/LLM, and FAISS.

## Features

- Multi-format document ingestion: PDF, DOCX, CSV, PPTX
- Multi-file upload and batch processing
- Parsing + text extraction for each supported file type
- Chunking with metadata (`source`, `chunk_id`)
- Persistent FAISS vector storage
- Retrieval-augmented question answering (RAG)
- Source citation in answers
- Streamlit UI with full pages: Overview, Upload, Ask, Documents, History

## Project Structure

- backend/file_parser.py
- backend/text_chunker.py
- backend/vector_store.py
- backend/rag_pipeline.py
- backend/main.py
- parsers/pdf_parser.py
- parsers/docx_parser.py
- parsers/csv_parser.py
- parsers/pptx_parser.py
- frontend/streamlit_app.py
- data/uploads/
- vector_db/

## Prerequisites

- Python 3.10+
- OpenAI API key

## Setup

1. Create and activate virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set environment variable:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Optional model settings:

```powershell
$env:OPENAI_MODEL="gpt-4o-mini"
$env:EMBEDDING_MODEL="text-embedding-3-small"
```

## Run Backend (FastAPI)

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

API endpoints:

- `POST /upload` - Upload and index documents
- `GET /ask?query=...` - Ask questions against indexed documents
- `GET /system/status` - Backend diagnostics and system status
- `GET /documents` - Uploaded document registry

## Run Frontend (Streamlit)

In another terminal:

```powershell
streamlit run frontend/streamlit_app.py
```

## Usage

1. Open Streamlit app in your browser.
2. Use **Overview** to verify backend and key status.
3. Use **Upload** to process one or more documents.
4. Use **Ask** to query indexed content and view citations.
5. Use **Documents** to inspect uploaded file registry.
6. Use **History** to review previous questions and answers.

## Notes for Production

- Add authentication and rate limiting to API.
- Restrict CORS origins in `backend/main.py`.
- Use a managed/vector DB service for larger workloads.
- Add request logging and structured monitoring.
- Add unit/integration tests and CI pipeline.
