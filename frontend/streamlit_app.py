from typing import Any

import requests
import streamlit as st


def inject_styles() -> None:
    """Apply a dark, product-style visual system to the Streamlit app."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(34, 197, 94, 0.08), transparent 28%),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.10), transparent 24%),
                linear-gradient(180deg, #0b1020 0%, #0f172a 52%, #111827 100%);
            color: #e5eefb;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.95), rgba(17, 24, 39, 0.96));
            border-right: 1px solid rgba(148, 163, 184, 0.15);
        }
        [data-testid="stSidebar"] * {
            color: #e5eefb;
        }
        .hero-card,
        .section-card,
        .result-card,
        .history-shell,
        .status-chip,
        .doc-pill,
        .chat-bubble-user,
        .chat-bubble-assistant {
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
        }
        .hero-card {
            padding: 1.4rem 1.5rem;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.90), rgba(30, 41, 59, 0.82));
            margin-bottom: 1.25rem;
        }
        .hero-kicker {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.14);
            color: #a7f3d0;
            font-size: 0.78rem;
            letter-spacing: 0.03em;
            margin-bottom: 0.9rem;
        }
        .hero-title {
            font-size: 3rem;
            line-height: 1.05;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin: 0;
            color: #f8fafc;
        }
        .hero-copy {
            margin-top: 0.85rem;
            color: #a5b4cc;
            font-size: 1.02rem;
            max-width: 54rem;
        }
        .metric-band {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.8rem;
            margin: 1rem 0 1.2rem 0;
        }
        .metric-card {
            background: rgba(15, 23, 42, 0.64);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 18px;
            padding: 1rem 1rem 0.85rem 1rem;
        }
        .metric-label {
            color: #8fa3bf;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-value {
            color: #f8fafc;
            font-size: 1.6rem;
            font-weight: 700;
            margin-top: 0.35rem;
        }
        .section-card,
        .result-card,
        .history-shell {
            background: rgba(15, 23, 42, 0.76);
            border-radius: 22px;
            padding: 1.15rem 1.15rem 1.25rem 1.15rem;
            backdrop-filter: blur(8px);
        }
        .section-title {
            margin: 0 0 0.35rem 0;
            font-size: 1.28rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .section-copy {
            margin: 0 0 1rem 0;
            color: #9fb0c8;
            font-size: 0.95rem;
        }
        .status-chip {
            display: inline-block;
            margin: 0.3rem 0.4rem 0 0;
            padding: 0.45rem 0.72rem;
            border-radius: 999px;
            background: rgba(30, 41, 59, 0.82);
            font-size: 0.84rem;
            color: #d7e2f0;
        }
        .doc-pill {
            display: inline-block;
            margin: 0.35rem 0.45rem 0 0;
            padding: 0.5rem 0.76rem;
            border-radius: 999px;
            background: rgba(12, 18, 33, 0.92);
            color: #dce8f8;
            font-size: 0.88rem;
        }
        .answer-text {
            color: #eaf2ff;
            line-height: 1.75;
            font-size: 1rem;
        }
        .citation-list {
            margin-top: 0.8rem;
            color: #d7e2f0;
        }
        .citation-list li {
            margin-bottom: 0.35rem;
        }
        .chat-bubble-user,
        .chat-bubble-assistant {
            padding: 0.95rem 1rem;
            border-radius: 18px;
            margin-bottom: 0.65rem;
            line-height: 1.7;
        }
        .chat-bubble-user {
            background: linear-gradient(135deg, rgba(8, 47, 73, 0.95), rgba(12, 74, 110, 0.82));
            color: #ebf8ff;
            margin-left: 12%;
        }
        .chat-bubble-assistant {
            background: linear-gradient(135deg, rgba(22, 101, 52, 0.20), rgba(15, 23, 42, 0.92));
            color: #eefbf3;
            margin-right: 12%;
        }
        .bubble-label {
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #9dd7ff;
            margin-bottom: 0.45rem;
            font-weight: 700;
        }
        .assistant-label {
            color: #9ae6b4;
        }
        .empty-state {
            color: #94a3b8;
            text-align: center;
            padding: 1.6rem 0.5rem;
        }
        .stTextInput input,
        .stTextArea textarea,
        .stFileUploader section,
        .stSelectbox div[data-baseweb="select"] > div,
        .stNumberInput input {
            background: rgba(15, 23, 42, 0.86) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(148, 163, 184, 0.16) !important;
            border-radius: 16px !important;
        }
        .stButton > button {
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.12);
            background: linear-gradient(135deg, #0f766e, #155e75);
            color: #f8fafc;
            font-weight: 700;
            min-height: 3rem;
        }
        .stButton > button:hover {
            border-color: rgba(103, 232, 249, 0.35);
            color: #ffffff;
        }
        .stButton > button:disabled {
            opacity: 0.45;
        }
        @media (max-width: 900px) {
            .hero-title {
                font-size: 2.2rem;
            }
            .metric-band {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .chat-bubble-user,
            .chat-bubble-assistant {
                margin-left: 0;
                margin-right: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session_state() -> None:
    """Initialize frontend state used across reruns."""
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("uploaded_documents", [])
    st.session_state.setdefault("last_upload_result", None)
    st.session_state.setdefault("latest_result", None)


def extract_error(exc: requests.RequestException) -> str:
    """Convert backend and HTTP errors into short user-facing messages."""
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            payload = response.json()
            if isinstance(payload, dict) and payload.get("detail"):
                return str(payload["detail"])
        except ValueError:
            pass
    return "Unable to complete the request. Check the backend URL and try again."


def upload_documents(api_url: str, files: list[Any]) -> dict[str, Any]:
    """Send uploaded files to the FastAPI backend for processing."""
    file_payload = [
        ("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type))
        for uploaded_file in files
    ]
    response = requests.post(f"{api_url}/upload", files=file_payload, timeout=180)
    response.raise_for_status()
    return response.json()


def ask_question(api_url: str, query: str) -> dict[str, Any]:
    """Send the user's query to the FastAPI backend and return the answer."""
    response = requests.get(f"{api_url}/ask", params={"query": query}, timeout=180)
    response.raise_for_status()
    return response.json()


def render_header() -> None:
    """Render the product hero section."""
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">RAG • Document AI • Multi-Format Search</div>
            <h1 class="hero-title">RAG-Based Universal Document Intelligence System</h1>
            <p class="hero-copy">
                Upload knowledge sources, ask grounded questions, and review citation-backed answers in a streamlined AI workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics() -> None:
    """Display compact product metrics near the top of the page."""
    upload_count = len(st.session_state.uploaded_documents)
    chat_count = len(st.session_state.chat_history)
    latest_sources = 0
    if st.session_state.latest_result:
        latest_sources = len(st.session_state.latest_result.get("sources", []))

    st.markdown(
        f"""
        <div class="metric-band">
            <div class="metric-card">
                <div class="metric-label">Uploaded Docs</div>
                <div class="metric-value">{upload_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Questions Asked</div>
                <div class="metric-value">{chat_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Supported Formats</div>
                <div class="metric-value">4</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Latest Citations</div>
                <div class="metric-value">{latest_sources}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    """Render sidebar settings and return the configured backend URL."""
    with st.sidebar:
        st.markdown("## Control Center")
        api_url = st.text_input("Backend API URL", value="http://localhost:8000")
        st.markdown("### Capabilities")
        st.markdown("- PDF, DOCX, CSV, PPTX upload")
        st.markdown("- Citation-backed answers")
        st.markdown("- Session chat memory")
        st.markdown("### Session Stats")
        st.markdown(
            f"""
            <div class="status-chip">📁 {len(st.session_state.uploaded_documents)} documents</div>
            <div class="status-chip">💬 {len(st.session_state.chat_history)} chat turns</div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Point this URL to your FastAPI server if it is running on a different host or port.")
    return api_url.rstrip("/")


def render_upload_section(api_url: str) -> None:
    """Render upload UI and process documents through the backend API."""
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">📂 Upload</div>
            <div class="section-copy">Add multiple knowledge files, send them to the backend, and build the retrieval index.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Choose one or more files",
        type=["pdf", "docx", "csv", "pptx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.markdown("#### Selected Documents")
        pills = "".join(
            f'<span class="doc-pill">📄 {uploaded_file.name}</span>'
            for uploaded_file in uploaded_files
        )
        st.markdown(pills, unsafe_allow_html=True)

    process_disabled = not uploaded_files
    if st.button("Process Documents", use_container_width=True, disabled=process_disabled):
        with st.spinner("Indexing documents and generating embeddings..."):
            try:
                result = upload_documents(api_url=api_url, files=uploaded_files)
                st.session_state.last_upload_result = result

                successful_files = [
                    item.get("file")
                    for item in result.get("results", [])
                    if item.get("status") == "processed" and item.get("file")
                ]
                for file_name in successful_files:
                    if file_name not in st.session_state.uploaded_documents:
                        st.session_state.uploaded_documents.append(file_name)

                st.success(result.get("message", "Documents processed successfully."))
            except requests.RequestException as exc:
                st.error(extract_error(exc))

    if not uploaded_files:
        st.info("Upload at least one file to enable processing.")

    if st.session_state.last_upload_result:
        result = st.session_state.last_upload_result
        st.markdown(f"**Chunks added:** {result.get('total_chunks_added', 0)}")
        for item in result.get("results", []):
            if item.get("status") == "processed":
                st.success(f"{item.get('file')} processed successfully with {item.get('chunks', 0)} chunks.")
            else:
                st.error(f"{item.get('file')} failed: {item.get('reason', 'Unknown error')}")

    st.markdown("#### Uploaded Documents")
    if st.session_state.uploaded_documents:
        pills = "".join(
            f'<span class="doc-pill">🗂️ {file_name}</span>'
            for file_name in st.session_state.uploaded_documents
        )
        st.markdown(pills, unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state">No documents uploaded in this session yet.</div>', unsafe_allow_html=True)


def render_ask_section(api_url: str) -> None:
    """Render query UI and request answers from the backend."""
    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">💬 Ask</div>
            <div class="section-copy">Ask grounded questions about the processed documents and receive citation-backed responses.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    query = st.text_area(
        "Ask a question about your documents",
        height=120,
        placeholder="What are the key points across the uploaded files?",
        label_visibility="collapsed",
    )

    if not st.session_state.uploaded_documents:
        st.caption("No documents uploaded in this session yet. If your backend already has indexed documents, you can still ask a question.")

    ask_disabled = not query.strip()
    if st.button("Ask", use_container_width=True, disabled=ask_disabled):
        with st.spinner("Searching relevant chunks and drafting an answer..."):
            try:
                result = ask_question(api_url=api_url, query=query.strip())
                answer = result.get("answer", "No answer returned.")
                sources = result.get("sources", [])
                st.session_state.latest_result = {
                    "question": query.strip(),
                    "answer": answer,
                    "sources": sources,
                }
                st.session_state.chat_history.append(st.session_state.latest_result.copy())
                st.success("Answer ready")
            except requests.RequestException as exc:
                st.error(extract_error(exc))

    if not query.strip():
        st.info("Enter a question to enable querying.")


def render_results_section() -> None:
    """Render the latest answer and its citations."""
    st.markdown(
        """
        <div class="result-card">
            <div class="section-title">✨ Results</div>
            <div class="section-copy">The latest answer and the source documents used to support it.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    latest_result = st.session_state.latest_result
    if not latest_result:
        st.markdown(
            '<div class="empty-state">No answer yet. Process documents and ask a question to populate this panel.</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(f"### {latest_result['question']}")
    st.markdown(
        f'<div class="answer-text">{latest_result["answer"]}</div>',
        unsafe_allow_html=True,
    )

    sources = latest_result.get("sources", [])
    if sources:
        source_items = "".join(f"<li>{source}</li>" for source in sources)
        st.markdown(
            f'<div class="citation-list"><strong>Sources</strong><ul>{source_items}</ul></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No citations were returned for the latest answer.")


def render_history_section() -> None:
    """Render session chat history using message-style bubbles."""
    st.markdown(
        """
        <div class="history-shell">
            <div class="section-title">🕘 Chat History</div>
            <div class="section-copy">A session-based timeline of previous questions and answers.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.chat_history:
        st.markdown(
            '<div class="empty-state">Your conversation history will appear here after the first successful query.</div>',
            unsafe_allow_html=True,
        )
        return

    for item in reversed(st.session_state.chat_history):
        st.markdown(
            f"""
            <div class="chat-bubble-user">
                <div class="bubble-label">User</div>
                <div>{item['question']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        citations = ""
        if item.get("sources"):
            citation_markup = "".join(f"<li>{source}</li>" for source in item["sources"])
            citations = f"<div class='citation-list'><strong>Sources</strong><ul>{citation_markup}</ul></div>"

        st.markdown(
            f"""
            <div class="chat-bubble-assistant">
                <div class="bubble-label assistant-label">Assistant</div>
                <div>{item['answer']}</div>
                {citations}
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Render the complete professional Streamlit frontend for the RAG system."""
    st.set_page_config(
        page_title="RAG-Based Universal Document Intelligence",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()
    inject_styles()
    api_url = render_sidebar()

    render_header()
    render_metrics()

    left_column, right_column = st.columns([1.05, 1.35], gap="large")

    with left_column:
        render_upload_section(api_url)

    with right_column:
        render_ask_section(api_url)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_results_section()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    render_history_section()


if __name__ == "__main__":
    main()