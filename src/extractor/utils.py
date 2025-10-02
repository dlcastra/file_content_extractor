import io

import fitz


def extract_first_page_text_from_pdf_bytes(file_bytes: bytes | io.BytesIO) -> str:
    """Extract text from the first page of a PDF file given as bytes or a BytesIO object."""

    doc = fitz.open(stream=file_bytes, filetype="pdf")
    if doc.page_count < 1:
        return ""
    page = doc.load_page(0)
    text = page.get_text()

    return text.strip()
