from typing import Any
from datetime import datetime
import time
import json

import requests
import streamlit as st


# ─── Constants ───────────────────────────────────────────────────────────────

SUPPORTED_FORMATS = ["pdf", "docx", "csv", "pptx"]
FORMAT_ICONS = {".pdf": "📕", ".docx": "📝", ".csv": "📊", ".pptx": "📎"}
DEFAULT_API_URL = "http://localhost:8000"

EXAMPLE_QUESTIONS = [
    "What are the key findings across all uploaded documents?",
    "Summarize the main points from the uploaded files.",
    "What data trends can be observed?",
    "List all important dates or deadlines mentioned.",
    "What recommendations are provided?",
]


# ─── Styles ──────────────────────────────────────────────────────────────────

def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        :root {
            --bg-primary: #0a0f1e;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.85);
            --bg-card-hover: rgba(30, 41, 59, 0.92);
            --accent-emerald: #10b981;
            --accent-cyan: #06b6d4;
            --accent-violet: #8b5cf6;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-subtle: rgba(148, 163, 184, 0.12);
            --border-glow: rgba(6, 182, 212, 0.25);
            --glass: rgba(15, 23, 42, 0.72);
            --shadow-lg: 0 24px 64px rgba(0, 0, 0, 0.35);
        }

        *, *::before, *::after { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

        .stApp {
            background:
                radial-gradient(ellipse at 10% 0%, rgba(16, 185, 129, 0.07) 0%, transparent 50%),
                radial-gradient(ellipse at 90% 0%, rgba(6, 182, 212, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 100%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
                linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(10, 15, 30, 0.98), rgba(17, 24, 39, 0.97));
            border-right: 1px solid var(--border-subtle);
        }
        [data-testid="stSidebar"] * { color: var(--text-primary); }

        .sidebar-brand {
            text-align: center;
            padding: 1.5rem 0 1rem 0;
        }
        .sidebar-brand-icon {
            font-size: 2.8rem;
            display: block;
            margin-bottom: 0.5rem;
            filter: drop-shadow(0 0 12px rgba(6, 182, 212, 0.4));
            animation: pulse-glow 3s ease-in-out infinite;
        }
        @keyframes pulse-glow {
            0%, 100% { filter: drop-shadow(0 0 12px rgba(6, 182, 212, 0.4)); }
            50% { filter: drop-shadow(0 0 20px rgba(6, 182, 212, 0.7)); }
        }
        .sidebar-brand-title {
            font-size: 1.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #06b6d4, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sidebar-brand-sub {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 0.2rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .sidebar-section-label {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
            margin: 1.2rem 0 0.4rem 0;
            font-weight: 700;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.5rem 0.7rem;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-subtle);
            margin-bottom: 0.35rem;
            font-size: 0.82rem;
            transition: all 0.3s ease;
        }
        .status-indicator:hover {
            border-color: var(--border-glow);
            background: rgba(15, 23, 42, 0.8);
        }
        .status-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .status-dot.online {
            background: #10b981;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
            animation: status-pulse 2s ease-in-out infinite;
        }
        .status-dot.offline { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.6); }
        .status-dot.warning { background: #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.6); }

        @keyframes status-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.2); }
        }

        /* ── Hero ── */
        .hero-section {
            padding: 2.2rem 2rem 1.6rem 2rem;
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(16, 185, 129, 0.06)),
                var(--bg-card);
            border: 1px solid var(--border-subtle);
            box-shadow: var(--shadow-lg);
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
            animation: slide-in-down 0.6s ease-out;
        }
        @keyframes slide-in-down {
            from { opacity: 0; transform: translateY(-15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(6, 182, 212, 0.08), transparent 70%);
            border-radius: 50%;
            animation: float-bg 8s ease-in-out infinite;
        }
        @keyframes float-bg {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(-20px, 15px); }
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.85rem;
            border-radius: 999px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #6ee7b7;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2.4rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 1.1;
            margin: 0;
            background: linear-gradient(135deg, #f1f5f9 30%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-description {
            margin-top: 0.85rem;
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
            max-width: 48rem;
        }

        /* ── Metrics ── */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background: var(--glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 1rem;
            transition: all 0.3s ease;
            animation: fade-in-up 0.5s ease-out both;
        }
        .metric-card:nth-child(1) { animation-delay: 0.1s; }
        .metric-card:nth-child(2) { animation-delay: 0.15s; }
        .metric-card:nth-child(3) { animation-delay: 0.2s; }
        .metric-card:nth-child(4) { animation-delay: 0.25s; }
        .metric-card:nth-child(5) { animation-delay: 0.3s; }

        @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .metric-card:hover {
            border-color: var(--border-glow);
            transform: translateY(-3px);
            box-shadow: 0 8px 32px rgba(6, 182, 212, 0.12);
        }
        .metric-icon { font-size: 1.3rem; margin-bottom: 0.4rem; }
        .metric-value {
            font-size: 1.7rem;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1.1;
        }
        .metric-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin-top: 0.25rem;
            font-weight: 600;
        }

        /* ── Section Cards ── */
        .section-card {
            background: var(--glass);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            padding: 1.4rem;
            box-shadow: var(--shadow-lg);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        .section-card:hover {
            border-color: var(--border-glow);
        }
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 0.5rem;
        }
        .section-icon {
            width: 36px; height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
        }
        .icon-upload { background: rgba(139, 92, 246, 0.15); }
        .icon-ask { background: rgba(6, 182, 212, 0.15); }
        .icon-results { background: rgba(16, 185, 129, 0.15); }
        .icon-history { background: rgba(245, 158, 11, 0.15); }
        .icon-docs { background: rgba(244, 63, 94, 0.15); }
        .icon-settings { background: rgba(139, 92, 246, 0.15); }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0;
        }
        .section-subtitle {
            font-size: 0.82rem;
            color: var(--text-muted);
            margin: 0 0 0.8rem 0;
        }

        /* ── File Pills ── */
        .file-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            margin: 0.25rem 0.3rem 0 0;
            padding: 0.4rem 0.75rem;
            border-radius: 999px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            font-size: 0.8rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .file-pill:hover {
            border-color: var(--border-glow);
            background: rgba(30, 41, 59, 0.95);
        }

        /* ── Document Cards ── */
        .doc-card {
            background: var(--glass);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
            animation: fade-in-up 0.4s ease-out both;
        }
        .doc-card:hover {
            border-color: var(--border-glow);
            transform: translateX(4px);
            background: var(--bg-card-hover);
        }
        .doc-card-left {
            display: flex;
            align-items: center;
            gap: 0.7rem;
        }
        .doc-card-icon {
            font-size: 1.6rem;
            width: 40px; height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: rgba(6, 182, 212, 0.1);
        }
        .doc-card-name {
            font-weight: 600;
            color: var(--text-primary);
            font-size: 0.88rem;
        }
        .doc-card-meta {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 0.15rem;
        }

        /* ── Chat Bubbles ── */
        .chat-user {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.12), rgba(8, 47, 73, 0.9));
            border: 1px solid rgba(6, 182, 212, 0.18);
            border-radius: 18px 18px 4px 18px;
            padding: 1rem 1.1rem;
            margin: 0.5rem 0 0.5rem 15%;
            color: var(--text-primary);
            line-height: 1.7;
            animation: slide-in-right 0.4s ease-out;
        }
        @keyframes slide-in-right {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .chat-assistant {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), var(--bg-card));
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 18px 18px 18px 4px;
            padding: 1rem 1.1rem;
            margin: 0.5rem 15% 0.5rem 0;
            color: var(--text-primary);
            line-height: 1.7;
            animation: slide-in-left 0.4s ease-out;
        }
        @keyframes slide-in-left {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .chat-role {
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .chat-role-user { color: #67e8f9; }
        .chat-role-ai { color: #6ee7b7; }

        /* ── Answer Card ── */
        .answer-card {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.06), var(--bg-card));
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 18px;
            padding: 1.2rem;
            margin-top: 0.6rem;
            animation: fade-in-up 0.5s ease-out;
        }
        .answer-text {
            color: var(--text-primary);
            line-height: 1.8;
            font-size: 0.95rem;
        }
        .citation-tag {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.3rem 0.6rem;
            border-radius: 8px;
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.2);
            color: #67e8f9;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.25rem 0.3rem 0 0;
            transition: all 0.2s ease;
        }
        .citation-tag:hover {
            background: rgba(6, 182, 212, 0.2);
            transform: translateY(-1px);
        }

        /* ── Timing Badge ── */
        .timing-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            background: rgba(139, 92, 246, 0.12);
            border: 1px solid rgba(139, 92, 246, 0.2);
            color: #c4b5fd;
            font-size: 0.72rem;
            font-weight: 600;
            margin-top: 0.5rem;
        }

        /* ── Suggestion Chips ── */
        .suggestion-chip {
            display: inline-block;
            padding: 0.45rem 0.9rem;
            border-radius: 999px;
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            font-size: 0.8rem;
            margin: 0.25rem 0.3rem 0 0;
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .suggestion-chip:hover {
            border-color: var(--accent-cyan);
            color: var(--text-primary);
            background: rgba(6, 182, 212, 0.1);
            transform: translateY(-1px);
        }

        /* ── Empty States ── */
        .empty-state {
            text-align: center;
            padding: 2.5rem 1rem;
            color: var(--text-muted);
            font-size: 0.88rem;
        }
        .empty-state-icon { font-size: 2.5rem; margin-bottom: 0.6rem; display: block; opacity: 0.4; }
        .empty-state-hint {
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-top: 0.6rem;
            opacity: 0.7;
        }

        /* ── Config Item ── */
        .config-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.65rem 0.9rem;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border-subtle);
            margin-bottom: 0.4rem;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }
        .config-item:hover { border-color: var(--border-glow); }
        .config-key { color: var(--text-muted); font-weight: 600; }
        .config-val { color: var(--text-primary); font-weight: 500; font-family: monospace !important; }

        /* ── Buttons ── */
        .stButton > button {
            border-radius: 14px;
            border: 1px solid var(--border-subtle);
            background: linear-gradient(135deg, #0d9488, #0891b2);
            color: #f8fafc;
            font-weight: 700;
            min-height: 2.8rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(13, 148, 136, 0.2);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 24px rgba(13, 148, 136, 0.35);
            border-color: rgba(103, 232, 249, 0.4);
        }
        .stButton > button:disabled { opacity: 0.4; transform: none; box-shadow: none; }

        /* ── Inputs ── */
        .stTextInput input,
        .stTextArea textarea,
        .stFileUploader section,
        .stSelectbox div[data-baseweb="select"] > div,
        .stNumberInput input {
            background: rgba(15, 23, 42, 0.85) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 14px !important;
            transition: border-color 0.3s ease !important;
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: var(--border-glow) !important;
            box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.1) !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background: var(--glass);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            color: var(--text-secondary);
            font-weight: 600;
            padding: 0.5rem 1.2rem;
            transition: all 0.3s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            border-color: var(--border-glow);
            color: var(--text-primary);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(16, 185, 129, 0.1)) !important;
            border-color: rgba(6, 182, 212, 0.3) !important;
            color: var(--text-primary) !important;
        }
        .stTabs [data-baseweb="tab-highlight"] {
            background: transparent !important;
        }
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }

        /* ── Responsive ── */
        @media (max-width: 768px) {
            .hero-title { font-size: 1.8rem; }
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .chat-user { margin-left: 5%; }
            .chat-assistant { margin-right: 5%; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── Session State ───────────────────────────────────────────────────────────

def init_session_state() -> None:
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("uploaded_documents", [])
    st.session_state.setdefault("last_upload_result", None)
    st.session_state.setdefault("latest_result", None)
    st.session_state.setdefault("backend_status", None)


# ─── API Helpers ─────────────────────────────────────────────────────────────

def check_backend(api_url: str) -> dict | None:
    try:
        resp = requests.get(f"{api_url}/system/status", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def fetch_documents(api_url: str) -> list[dict]:
    try:
        resp = requests.get(f"{api_url}/documents", timeout=10)
        resp.raise_for_status()
        return resp.json().get("documents", [])
    except Exception:
        return []


def upload_documents(api_url: str, files: list[Any]) -> dict[str, Any]:
    payload = [
        ("files", (f.name, f.getvalue(), f.type))
        for f in files
    ]
    resp = requests.post(f"{api_url}/upload", files=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()


def ask_question_api(api_url: str, query: str) -> dict[str, Any]:
    resp = requests.get(f"{api_url}/ask", params={"query": query}, timeout=180)
    resp.raise_for_status()
    return resp.json()


def delete_document_api(api_url: str, stored_name: str) -> dict:
    resp = requests.delete(f"{api_url}/documents/{stored_name}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def delete_all_documents_api(api_url: str) -> dict:
    resp = requests.delete(f"{api_url}/documents", timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_error(exc: requests.RequestException) -> str:
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            payload = response.json()
            if isinstance(payload, dict) and payload.get("detail"):
                return str(payload["detail"])
        except ValueError:
            pass
    return "Unable to reach the backend. Please verify the API server is running."


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def format_time_ago(timestamp: float) -> str:
    """Format a Unix timestamp as a human-readable 'time ago' string."""
    diff = time.time() - timestamp
    if diff < 60:
        return "just now"
    elif diff < 3600:
        mins = int(diff / 60)
        return f"{mins}m ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours}h ago"
    else:
        days = int(diff / 86400)
        return f"{days}d ago"


# ─── Sidebar ─────────────────────────────────────────────────────────────────

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <span class="sidebar-brand-icon">🧠</span>
                <div class="sidebar-brand-title">DocIntel AI</div>
                <div class="sidebar-brand-sub">RAG Document Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">⚡ Connection</div>', unsafe_allow_html=True)
        api_url = st.text_input("Backend API URL", value=DEFAULT_API_URL, label_visibility="collapsed")
        api_url = api_url.strip().rstrip("/")

        # Live backend check
        status = check_backend(api_url)
        st.session_state.backend_status = status

        if status:
            groq_key_set = status.get("groq_api_key_set", False)
            groq_reachable = status.get("groq_reachable", False)
            index_exists = status.get("vector_index_exists", False)
            file_count = status.get("uploaded_file_count", 0)
            total_chunks = status.get("total_chunks", 0)
            llm_model = status.get("llm_model", "llama-3.3-70b-versatile")
            embed_model = status.get("embedding_model", "all-MiniLM-L6-v2")

            groq_status = "online" if groq_reachable else ("warning" if groq_key_set else "offline")
            groq_label = "Groq Connected" if groq_reachable else ("Key Set (Unreachable)" if groq_key_set else "API Key Missing")

            st.markdown(
                f"""
                <div class="status-indicator"><span class="status-dot online"></span> Backend Online</div>
                <div class="status-indicator"><span class="status-dot {groq_status}"></span> {groq_label}</div>
                <div class="status-indicator"><span class="status-dot {'online' if index_exists else 'warning'}"></span> Vector Index {'Ready' if index_exists else 'Empty'}</div>
                <div class="status-indicator"><span class="status-dot online"></span> {file_count} file{'s' if file_count != 1 else ''} • {total_chunks} chunks</div>
                <div class="status-indicator">🤖 LLM: {llm_model}</div>
                <div class="status-indicator">📐 Embed: {embed_model}</div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-indicator"><span class="status-dot offline"></span> Backend Offline</div>',
                unsafe_allow_html=True,
            )
            if st.button("🔄 Retry Connection", use_container_width=True):
                st.rerun()

        st.markdown('<div class="sidebar-section-label">📋 Session</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="status-indicator">📁 {len(st.session_state.uploaded_documents)} uploaded this session</div>
            <div class="status-indicator">💬 {len(st.session_state.chat_history)} question{'s' if len(st.session_state.chat_history) != 1 else ''} asked</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-section-label">📂 Supported Formats</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="status-indicator">📕 PDF &nbsp;│&nbsp; 📝 DOCX &nbsp;│&nbsp; 📊 CSV &nbsp;│&nbsp; 📎 PPTX</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.caption("v2.0 — Powered by Groq + HuggingFace")

    return api_url


# ─── Hero ────────────────────────────────────────────────────────────────────

def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-badge">⚡ RAG-Powered • Groq Cloud AI • Citation-Backed</div>
            <h1 class="hero-title">Document Intelligence System</h1>
            <p class="hero-description">
                Upload knowledge documents, ask grounded questions across your entire corpus,
                and receive AI-generated answers with precise source citations — all in real time.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Metrics ─────────────────────────────────────────────────────────────────

def render_metrics() -> None:
    upload_count = len(st.session_state.uploaded_documents)
    chat_count = len(st.session_state.chat_history)
    latest_sources = 0
    last_time_ms = "—"
    if st.session_state.latest_result:
        latest_sources = len(st.session_state.latest_result.get("sources", []))
        ms = st.session_state.latest_result.get("processing_time_ms")
        if ms is not None:
            last_time_ms = f"{ms}ms"

    backend_status = "🟢" if st.session_state.backend_status else "🔴"

    total_chunks = 0
    if st.session_state.backend_status:
        total_chunks = st.session_state.backend_status.get("total_chunks", 0)

    st.markdown(
        f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon">📁</div>
                <div class="metric-value">{upload_count}</div>
                <div class="metric-label">Documents</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🧩</div>
                <div class="metric-value">{total_chunks}</div>
                <div class="metric-label">Chunks</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">💬</div>
                <div class="metric-value">{chat_count}</div>
                <div class="metric-label">Questions</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">⚡</div>
                <div class="metric-value">{last_time_ms}</div>
                <div class="metric-label">Last Response</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">{backend_status}</div>
                <div class="metric-value">{'ON' if st.session_state.backend_status else 'OFF'}</div>
                <div class="metric-label">Backend</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Upload Tab ──────────────────────────────────────────────────────────────

def render_upload_tab(api_url: str) -> None:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-header">
                <div class="section-icon icon-upload">📂</div>
                <h3 class="section-title">Upload Documents</h3>
            </div>
            <p class="section-subtitle">Drop your knowledge files here. They'll be parsed, chunked, embedded, and indexed automatically.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload files",
        type=SUPPORTED_FORMATS,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        pills = "".join(
            f'<span class="file-pill">{FORMAT_ICONS.get("." + f.name.rsplit(".", 1)[-1], "📄")} {f.name} <span style="color:var(--text-muted); font-size:0.72rem;">({format_size(f.size)})</span></span>'
            for f in uploaded_files
        )
        st.markdown(pills, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        process_btn = st.button(
            "⚡ Process & Index Documents",
            use_container_width=True,
            disabled=not uploaded_files,
        )
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    if process_btn and uploaded_files:
        progress_bar = st.progress(0, text="📦 Starting document processing...")

        try:
            progress_bar.progress(10, text="📤 Uploading files to backend...")
            result = upload_documents(api_url=api_url, files=uploaded_files)
            st.session_state.last_upload_result = result

            progress_bar.progress(50, text="🔬 Parsing and generating embeddings...")
            time.sleep(0.3)

            successful = [
                item.get("file")
                for item in result.get("results", [])
                if item.get("status") == "processed" and item.get("file")
            ]
            for fname in successful:
                if fname not in st.session_state.uploaded_documents:
                    st.session_state.uploaded_documents.append(fname)

            progress_bar.progress(100, text="✅ Processing complete!")
            time.sleep(0.5)
            progress_bar.empty()

            total_chunks = result.get("total_chunks_added", 0)
            processing_time = result.get("processing_time_ms", 0)
            st.success(f"🎉 Processed {len(successful)} file(s) into {total_chunks} chunks in {processing_time}ms!")

            for item in result.get("results", []):
                if item.get("status") == "processed":
                    st.info(f"✓ **{item.get('file')}** → {item.get('chunks', 0)} chunks")
                else:
                    st.error(f"✗ **{item.get('file')}** failed: {item.get('reason', 'Unknown error')}")

        except requests.RequestException as exc:
            progress_bar.empty()
            st.error(f"🚫 {extract_error(exc)}")

    if not uploaded_files:
        st.markdown(
            '<div class="empty-state"><span class="empty-state-icon">📂</span>Drop PDF, DOCX, CSV, or PPTX files above to begin<div class="empty-state-hint">Files are parsed, chunked, embedded, and indexed automatically</div></div>',
            unsafe_allow_html=True,
        )


# ─── Ask Tab ─────────────────────────────────────────────────────────────────

def render_ask_tab(api_url: str) -> None:
    # Show chat history in conversation style
    if st.session_state.chat_history:
        for item in st.session_state.chat_history:
            st.markdown(
                f"""
                <div class="chat-user">
                    <div class="chat-role chat-role-user">You</div>
                    <div>{item['question']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            citations = ""
            if item.get("sources"):
                tags = "".join(f'<span class="citation-tag">📎 {s}</span>' for s in item["sources"])
                citations = f'<div style="margin-top:0.6rem;">{tags}</div>'

            timing = ""
            ms = item.get("processing_time_ms")
            if ms is not None:
                timing = f'<div class="timing-badge">⚡ {ms}ms response time</div>'

            st.markdown(
                f"""
                <div class="chat-assistant">
                    <div class="chat-role chat-role-ai">AI Assistant</div>
                    <div>{item['answer']}</div>
                    {citations}
                    {timing}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty-state"><span class="empty-state-icon">💬</span>Start a conversation by asking a question below<div class="empty-state-hint">Your questions and AI answers will appear here as a conversation</div></div>',
            unsafe_allow_html=True,
        )

        # Show suggestion chips
        st.markdown("**💡 Try asking:**", unsafe_allow_html=True)
        cols = st.columns(2)
        for i, q in enumerate(EXAMPLE_QUESTIONS[:4]):
            with cols[i % 2]:
                if st.button(f"📌 {q[:50]}...", key=f"sug_{i}", use_container_width=True):
                    _run_question(api_url, q)
                    st.rerun()

    # Input area
    st.markdown("---")
    query = st.text_area(
        "Your question",
        height=80,
        placeholder="Type your question here... (e.g. What are the key findings?)",
        label_visibility="collapsed",
    )

    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        ask_disabled = not query or len(query.strip()) < 3
        ask_btn = st.button("🔍 Search & Answer", use_container_width=True, disabled=ask_disabled)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True, disabled=not st.session_state.chat_history):
            st.session_state.chat_history = []
            st.session_state.latest_result = None
            st.rerun()
    with col3:
        if st.button("📋 Export", use_container_width=True, disabled=not st.session_state.chat_history):
            export_text = _export_chat_history()
            st.download_button(
                "📥 Download",
                data=export_text,
                file_name="chat_history.md",
                mime="text/markdown",
                use_container_width=True,
            )

    if ask_btn and query and len(query.strip()) >= 3:
        _run_question(api_url, query.strip())
        st.rerun()


def _run_question(api_url: str, query: str) -> None:
    """Execute a question and store the result in session state."""
    try:
        result = ask_question_api(api_url=api_url, query=query)
        answer = result.get("answer", "No answer returned.")
        sources = result.get("sources", [])
        processing_time_ms = result.get("processing_time_ms")
        entry = {
            "question": query,
            "answer": answer,
            "sources": sources,
            "processing_time_ms": processing_time_ms,
        }
        st.session_state.latest_result = entry
        st.session_state.chat_history.append(entry.copy())
    except requests.RequestException as exc:
        st.session_state.chat_history.append({
            "question": query,
            "answer": f"❌ Error: {extract_error(exc)}",
            "sources": [],
            "processing_time_ms": None,
        })


def _export_chat_history() -> str:
    """Export chat history as markdown text."""
    lines = ["# DocIntel AI — Chat History\n"]
    for i, item in enumerate(st.session_state.chat_history, 1):
        lines.append(f"## Question {i}")
        lines.append(f"**Q:** {item['question']}\n")
        lines.append(f"**A:** {item['answer']}\n")
        if item.get("sources"):
            lines.append(f"**Sources:** {', '.join(item['sources'])}\n")
        if item.get("processing_time_ms"):
            lines.append(f"*Response time: {item['processing_time_ms']}ms*\n")
        lines.append("---\n")
    return "\n".join(lines)


# ─── Documents Tab ───────────────────────────────────────────────────────────

def render_documents_tab(api_url: str) -> None:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-header">
                <div class="section-icon icon-docs">📚</div>
                <h3 class="section-title">Document Registry</h3>
            </div>
            <p class="section-subtitle">All documents stored and indexed on the backend server.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    docs = fetch_documents(api_url)

    if not docs:
        st.markdown(
            '<div class="empty-state"><span class="empty-state-icon">📚</span>No documents stored on the server yet<div class="empty-state-hint">Upload documents in the Upload tab to get started</div></div>',
            unsafe_allow_html=True,
        )
        return

    # Header row with clear all button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{len(docs)} document{'s' if len(docs) != 1 else ''} stored**")
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
            try:
                delete_all_documents_api(api_url)
                st.session_state.uploaded_documents = []
                st.success("✅ All documents and vector index cleared!")
                time.sleep(1)
                st.rerun()
            except requests.RequestException as exc:
                st.error(f"🚫 {extract_error(exc)}")

    # Document cards
    for doc in docs:
        name = doc.get("name", "Unknown")
        stored_name = doc.get("stored_name", "")
        size = format_size(doc.get("size_bytes", 0))
        ext = "." + name.rsplit(".", 1)[-1] if "." in name else ""
        icon = FORMAT_ICONS.get(ext, "📄")
        uploaded_at = doc.get("uploaded_at")
        time_str = format_time_ago(uploaded_at) if uploaded_at else ""

        col_doc, col_del = st.columns([6, 1])
        with col_doc:
            st.markdown(
                f"""<div class="doc-card">
                    <div class="doc-card-left">
                        <div class="doc-card-icon">{icon}</div>
                        <div>
                            <div class="doc-card-name">{name}</div>
                            <div class="doc-card-meta">{size} • {time_str}</div>
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col_del:
            if st.button("🗑️", key=f"del_{stored_name}", help=f"Delete {name}"):
                try:
                    delete_document_api(api_url, stored_name)
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"🚫 {extract_error(exc)}")


# ─── History Tab ─────────────────────────────────────────────────────────────

def render_history_tab() -> None:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-header">
                <div class="section-icon icon-history">🕘</div>
                <h3 class="section-title">Chat History</h3>
            </div>
            <p class="section-subtitle">Your session conversation timeline with expandable details.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.chat_history:
        st.markdown(
            '<div class="empty-state"><span class="empty-state-icon">💬</span>Your conversation history will appear here after your first query<div class="empty-state-hint">Switch to the Ask tab to start asking questions</div></div>',
            unsafe_allow_html=True,
        )
        return

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{len(st.session_state.chat_history)} conversation{'s' if len(st.session_state.chat_history) != 1 else ''}**")
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.latest_result = None
            st.rerun()

    for i, item in enumerate(reversed(st.session_state.chat_history)):
        q_preview = item["question"][:80] + ("..." if len(item["question"]) > 80 else "")
        timing_str = f" • ⚡{item.get('processing_time_ms')}ms" if item.get("processing_time_ms") else ""

        with st.expander(f"💬 {q_preview}{timing_str}", expanded=(i == 0)):
            st.markdown(
                f"""
                <div class="chat-user">
                    <div class="chat-role chat-role-user">You</div>
                    <div>{item['question']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            citations = ""
            if item.get("sources"):
                tags = "".join(f'<span class="citation-tag">📎 {s}</span>' for s in item["sources"])
                citations = f'<div style="margin-top:0.6rem;">{tags}</div>'

            timing = ""
            ms = item.get("processing_time_ms")
            if ms is not None:
                timing = f'<div class="timing-badge">⚡ {ms}ms response time</div>'

            st.markdown(
                f"""
                <div class="chat-assistant">
                    <div class="chat-role chat-role-ai">AI Assistant</div>
                    <div>{item['answer']}</div>
                    {citations}
                    {timing}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ─── Settings Tab ────────────────────────────────────────────────────────────

def render_settings_tab(api_url: str) -> None:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-header">
                <div class="section-icon icon-settings">⚙️</div>
                <h3 class="section-title">System Configuration</h3>
            </div>
            <p class="section-subtitle">Current system configuration and diagnostics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    status = st.session_state.backend_status

    if not status:
        st.warning("⚠️ Backend is offline. Start the FastAPI server to see configuration.")
        return

    # System info
    st.markdown("#### 🔧 Infrastructure")
    configs = [
        ("LLM Provider", "Groq Cloud API"),
        ("LLM Model", status.get("llm_model", "—")),
        ("Embedding Provider", "HuggingFace (Local)"),
        ("Embedding Model", status.get("embedding_model", "—")),
        ("Vector Store", "FAISS (Persistent)"),
        ("Backend", status.get("backend", "—")),
    ]
    for key, val in configs:
        st.markdown(
            f'<div class="config-item"><span class="config-key">{key}</span><span class="config-val">{val}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### 📊 Storage Stats")
    stats = [
        ("Files Stored", str(status.get("uploaded_file_count", 0))),
        ("Total Chunks", str(status.get("total_chunks", 0))),
        ("Vector Index", "✅ Ready" if status.get("vector_index_exists") else "⚠️ Empty"),
        ("Groq API", "✅ Connected" if status.get("groq_reachable") else "❌ Unreachable"),
    ]
    for key, val in stats:
        st.markdown(
            f'<div class="config-item"><span class="config-key">{key}</span><span class="config-val">{val}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### 🔗 API Endpoints")
    endpoints = [
        ("Health Check", f"GET {api_url}/"),
        ("System Status", f"GET {api_url}/system/status"),
        ("Upload", f"POST {api_url}/upload"),
        ("Ask", f"GET {api_url}/ask?query=..."),
        ("Documents", f"GET {api_url}/documents"),
        ("Delete Doc", f"DELETE {api_url}/documents/{{name}}"),
    ]
    for key, val in endpoints:
        st.markdown(
            f'<div class="config-item"><span class="config-key">{key}</span><span class="config-val" style="font-size:0.75rem;">{val}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:var(--text-muted); font-size:0.78rem;">DocIntel AI v2.0 — Built with FastAPI, Streamlit, LangChain, Groq & HuggingFace</div>',
        unsafe_allow_html=True,
    )


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="DocIntel AI — RAG Document Intelligence",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    inject_styles()
    api_url = render_sidebar()

    render_hero()
    render_metrics()

    # ── Tabbed navigation ──
    tab_upload, tab_ask, tab_docs, tab_history, tab_settings = st.tabs([
        "📤 Upload",
        "💬 Ask",
        "📚 Documents",
        "🕘 History",
        "⚙️ Settings",
    ])

    with tab_upload:
        render_upload_tab(api_url)

    with tab_ask:
        render_ask_tab(api_url)

    with tab_docs:
        render_documents_tab(api_url)

    with tab_history:
        render_history_tab()

    with tab_settings:
        render_settings_tab(api_url)


if __name__ == "__main__":
    main()