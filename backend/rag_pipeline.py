import os
import logging

from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.vector_store import load_vector_store

logger = logging.getLogger(__name__)


def load_rag() -> ChatGroq:
    """Create and return the Groq chat model used in the RAG pipeline."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your .env file or environment variables."
        )
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=0,
    )


def _build_prompt(query: str, context: str) -> str:
    """Create the instruction prompt used for answer generation."""
    prompt_template = ChatPromptTemplate.from_template(
        """
You are an enterprise document intelligence assistant.
Answer the question using only the context below.
If the context does not contain the answer, say you do not know.

Context:
{context}

Question:
{query}
""".strip()
    )
    return prompt_template.format_messages(context=context, query=query)[0].content


def ask_question(query: str, k: int = 4) -> dict:
    """Run RAG for a query and return answer plus source citations."""
    vector_store = load_vector_store()
    if vector_store is None:
        raise FileNotFoundError(
            "Vector store not found. Upload and process documents first."
        )

    source_documents = vector_store.similarity_search(query, k=k)
    context = "\n\n".join(doc.page_content for doc in source_documents)

    model = load_rag()
    prompt = _build_prompt(query=query, context=context)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def invoke_model():
        return model.invoke(prompt)

    try:
        response = invoke_model()
        answer = response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        logger.error(f"Error invoking Groq model after retries: {exc}")
        raise

    sources: list[str] = []

    for document in source_documents:
        source_name = document.metadata.get("source", "unknown")
        if source_name not in sources:
            sources.append(source_name)

    return {"answer": answer, "sources": sources}