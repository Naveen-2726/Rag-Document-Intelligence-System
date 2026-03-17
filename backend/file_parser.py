from pathlib import Path

from parsers.csv_parser import parse_csv
from parsers.docx_parser import parse_docx
from parsers.pdf_parser import parse_pdf
from parsers.pptx_parser import parse_pptx

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".csv", ".pptx"}


def parse_file(file_path: str | Path) -> str:
    """Route a file path to the right parser based on its extension."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return parse_pdf(path)
    if extension == ".docx":
        return parse_docx(path)
    if extension == ".csv":
        return parse_csv(path)
    if extension == ".pptx":
        return parse_pptx(path)

    raise ValueError(f"Unsupported file format: {extension}")