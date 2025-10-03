from .docx_processor import DocxProcessor
from .pdf_processor import PDFProcessor
from .txt_processor import TXTProcessor


class GlobalProcessor(DocxProcessor, PDFProcessor, TXTProcessor):
    pass


__all__ = ["GlobalProcessor", "PDFProcessor", "TXTProcessor", "PDFProcessor"]
