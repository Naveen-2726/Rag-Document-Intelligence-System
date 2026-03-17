import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from backend.vector_store import load_vector_store, require_openai_api_key


def load_rag() -> ChatOpenAI:
    """Create and return the chat model used in the RAG pipeline."""
    require_openai_api_key()
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
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
    response = model.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    sources: list[str] = []

    for document in source_documents:
        source_name = document.metadata.get("source", "unknown")
        if source_name not in sources:
            sources.append(source_name)

    return {"answer": answer, "sources": sources}