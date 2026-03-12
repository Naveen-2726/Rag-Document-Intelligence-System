import docx

def parse_docx(file_path):

    doc = docx.Document(file_path)

    text = ""

    for para in doc.paragraphs:
        text += para.text

    return text