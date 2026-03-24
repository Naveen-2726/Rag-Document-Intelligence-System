import pytest
from unittest.mock import patch, MagicMock

from parsers.csv_parser import parse_csv
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from parsers.pptx_parser import parse_pptx


@patch("parsers.pdf_parser.PdfReader")
def test_parse_pdf(mock_reader_class):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Test PDF Content"
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_reader_class.return_value = mock_reader_instance

    result = parse_pdf("dummy.pdf")
    assert result == "Test PDF Content"


@patch("parsers.csv_parser.pd.read_csv")
def test_parse_csv(mock_read_csv):
    mock_df = MagicMock()
    mock_df.to_csv.return_value = "Column1,Column2\nVal1,Val2"
    mock_read_csv.return_value = mock_df

    result = parse_csv("dummy.csv")
    assert result == "Column1,Column2\nVal1,Val2"


@patch("parsers.docx_parser.docx.Document")
def test_parse_docx(mock_document_class):
    mock_doc = MagicMock()
    mock_para = MagicMock()
    mock_para.text = "Test DOCX Content"
    mock_doc.paragraphs = [mock_para]
    mock_doc.tables = []
    mock_document_class.return_value = mock_doc

    result = parse_docx("dummy.docx")
    assert result == "Test DOCX Content"


@patch("parsers.pptx_parser.Presentation")
def test_parse_pptx(mock_presentation_class):
    mock_slide = MagicMock()
    mock_shape = MagicMock()
    mock_shape.text = "Slide 1 Content"
    mock_slide.shapes = [mock_shape]
    mock_presentation = MagicMock()
    mock_presentation.slides = [mock_slide]
    mock_presentation_class.return_value = mock_presentation

    result = parse_pptx("dummy.pptx")
    # pptx_parser prepends 'Slide X: '
    assert "Slide 1 Content" in result
    assert result.startswith("Slide 1:")
