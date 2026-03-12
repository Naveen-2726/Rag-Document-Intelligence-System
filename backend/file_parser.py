import os

from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from parsers.csv_parser import parse_csv

def parse_file(file_path):

    ext = os.path.splitext(file_path)[1]

    if ext == ".pdf":
        return parse_pdf(file_path)

    elif ext == ".docx":
        return parse_docx(file_path)

    elif ext == ".csv":
        return parse_csv(file_path)

    else:
        raise ValueError("Unsupported file format")