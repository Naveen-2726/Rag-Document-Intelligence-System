from pathlib import Path

from pypdf import PdfReader


def parse_pdf(file_path: str | Path) -> str:
    """Extract and return text content from a PDF file path."""
    reader = PdfReader(str(file_path))
    chunks: list[str] = []
    for page in reader.pages:
        chunks.append(page.extract_text() or "")
    return "\n".join(chunks).strip()