from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(
    text: str,
    source: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[Document]:
    """Split raw text into LangChain documents with source metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(text)
    documents: list[Document] = []
    for index, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={"source": source, "chunk_id": index},
            )
        )

    return documents