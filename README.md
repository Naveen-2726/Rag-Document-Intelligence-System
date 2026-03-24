# 🧠 DocIntel AI — RAG Document Intelligence System

An AI-powered document intelligence system that lets you upload documents, ask questions about their content, and receive answers with source citations — powered by **Groq Cloud AI** and **HuggingFace embeddings**.

---

## 🚀 Features

- **Multi-Format Support** — Upload PDF, DOCX, CSV, and PPTX files
- **RAG Pipeline** — Retrieval-Augmented Generation for grounded, hallucination-free answers
- **Source Citations** — Every answer includes the exact documents it was sourced from
- **Ultra-Fast Inference** — Groq's LPU delivers answers in milliseconds
- **Document Management** — Upload, view, and delete documents with a single click
- **Chat History** — Full conversation timeline with export to Markdown
- **Real-Time Diagnostics** — System status, chunk count, response timing, and API health

---

## 🏗️ Architecture

```
┌──────────────────┐     HTTP      ┌───────────────────────────────────┐
│   Streamlit UI   │◄────────────►│       FastAPI Backend             │
│   (Port 8501)    │              │       (Port 8000)                 │
└──────────────────┘              │                                   │
                                  │  ┌─────────┐  ┌──────────────┐   │
                                  │  │ Parsers  │  │ Text Chunker │   │
                                  │  └────┬─────┘  └──────┬───────┘   │
                                  │       └───────┬───────┘           │
                                  │               ▼                   │
                                  │  ┌────────────────────────┐       │
                                  │  │   FAISS Vector Store   │       │
                                  │  │   + HuggingFace Embed  │       │
                                  │  └────────────────────────┘       │
                                  │               │                   │
                                  │               ▼                   │
                                  │  ┌────────────────────────┐       │
                                  │  │   Groq LLM (Cloud)     │       │
                                  │  │   llama-3.3-70b        │       │
                                  │  └────────────────────────┘       │
                                  └───────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq Cloud API (`llama-3.3-70b-versatile`) |
| Embeddings | HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`) — runs locally |
| Vector Store | FAISS (persistent, on-disk) |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Orchestration | LangChain |
| File Parsing | pypdf, python-docx, python-pptx, pandas |

---

## 📁 Project Structure

```
RAG_Document_Intelligence_System/
├── backend/
│   ├── main.py              # FastAPI app — routes, CORS, rate limiting
│   ├── rag_pipeline.py      # RAG logic — retrieval + Groq LLM answering
│   ├── vector_store.py      # FAISS index — embed, store, search, delete
│   ├── text_chunker.py      # Splits text into overlapping chunks
│   └── file_parser.py       # Routes files to format-specific parsers
├── parsers/
│   ├── pdf_parser.py        # PDF text extraction (pypdf)
│   ├── docx_parser.py       # DOCX extraction (python-docx)
│   ├── csv_parser.py        # CSV extraction (pandas)
│   └── pptx_parser.py       # PPTX extraction (python-pptx)
├── frontend/
│   └── streamlit_app.py     # Full UI — tabs, chat, documents, settings
├── tests/
│   ├── test_api.py          # API endpoint tests
│   ├── test_parsers.py      # Parser unit tests
│   └── test_chunker.py      # Chunker unit tests
├── data/uploads/             # Uploaded files stored here
├── vector_db/                # FAISS index persisted here
├── .env                      # API keys (gitignored)
├── requirements.txt          # Python dependencies
└── fix_and_run.ps1           # One-command startup script
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd RAG_Document_Intelligence_System
python -m venv clean_env
.\clean_env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Get your free API key at [console.groq.com](https://console.groq.com).

### 3. Run

**Option A — One command:**
```powershell
.\fix_and_run.ps1
```

**Option B — Manual:**
```powershell
# Terminal 1: Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
streamlit run frontend/streamlit_app.py
```

### 4. Open

- **Frontend:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

---

## 🔄 How It Works

### Document Upload
1. Upload a file (PDF/DOCX/CSV/PPTX)
2. File is parsed into raw text using format-specific extractors
3. Text is split into ~800-character overlapping chunks
4. Each chunk is embedded using HuggingFace (`all-MiniLM-L6-v2`)
5. Vectors are stored in a persistent FAISS index

### Asking Questions
1. Your question is embedded using the same model
2. FAISS finds the top-4 most similar chunks
3. Chunks are sent as context to Groq's `llama-3.3-70b-versatile`
4. The LLM generates an answer strictly from the context
5. Answer is returned with source citations and response time

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/system/status` | System diagnostics |
| `POST` | `/upload` | Upload and process documents |
| `GET` | `/ask?query=...` | Ask a question |
| `GET` | `/documents` | List all documents |
| `DELETE` | `/documents/{name}` | Delete a specific document |
| `DELETE` | `/documents` | Delete all documents + reset index |

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 📋 Requirements

- Python 3.10+
- Groq API key (free tier available)
- ~500MB disk for HuggingFace model (downloaded on first run)

---

*Built with FastAPI, Streamlit, LangChain, Groq & HuggingFace*
