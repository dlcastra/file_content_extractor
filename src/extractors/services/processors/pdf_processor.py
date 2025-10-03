import asyncio
import io

import fitz
from loguru import logger

from src.extractors.mixins.processors import ProcessorMixin
from src.extractors.services.schemas import ProcessedFileSchema
from src.extractors.utils import extract_first_page_text_from_pdf_bytes


class PDFProcessor(ProcessorMixin):
    async def process_pdf_bytes(self, file_bytes: bytes | io.BytesIO) -> ProcessedFileSchema:
        """
        Process PDF file bytes to extract text content.
        Uses base text extraction if text is found on the first page, otherwise uses OCR for pages with images.
        For base text extraction, PyMuPDF (fitz) is used and for OCR, Azure Cognitive Services is intended.

        Parameters:
            file_bytes: bytes or io.BytesIO - The PDF file content in bytes or BytesIO format.

        Returns:
            ProcessedFileSchema - The result of the processing, including success status and extracted text or
            reason for failure. For successful processing requires 'text' field, for failed processing requires 'reason' field.

            **Examples:**
                - ProcessedFileSchema(processed=True, text="Extracted text from PDF")
                - ProcessedFileSchema(processed=False, reason="Failed to extract text from the file")
        """

        logger.info("Starting PDF file processing")

        if not file_bytes:
            logger.info("Missed file bytes")
            return ProcessedFileSchema(processed=False, reason="Missed file bytes")

        first_page_text = await asyncio.to_thread(extract_first_page_text_from_pdf_bytes, file_bytes)

        extracted_file_content, processed = "", False
        if first_page_text:
            logger.info("First page text extracted successfully, using base text extraction")
            extracted_file_content, processed = await self._use_base_pdf_text_extraction(file_bytes)

        elif not first_page_text:
            logger.info("No text found on the first page, using OCR text extraction")
            extracted_file_content, processed = await self._use_ocr_text_extraction(file_bytes)

        if not processed:
            logger.info("Failed to extract text from the file")
            return ProcessedFileSchema(processed=processed, reason="Failed to extract text from the file")

        return ProcessedFileSchema(processed=processed, text=extracted_file_content)

    async def _use_base_pdf_text_extraction(self, file_bytes: bytes | io.BytesIO) -> tuple[str, bool]:
        """
        Extract text from PDF using PyMuPDF (fitz) library.
        This method reads the PDF file bytes and extracts text from all pages.
        If text extraction is successful, it returns the concatenated text from all pages.
        If any error occurs during the process, it logs the error and returns an empty string with a failure status.

        Parameters:
            file_bytes: bytes or io.BytesIO - The PDF file content in bytes or BytesIO format.

        Returns:
            tuple[str, bool] - A tuple containing the extracted text (or an empty string if extraction failed)
            and a boolean indicating success (True) or failure (False).

            **Examples:**
                - ("Extracted text from PDF", True)
                - ("", False)
        """

        try:
            logger.info(f"Starting text extraction from PDF file")
            doc = fitz.open("pdf", file_bytes.read())

            pages_text = ""
            for page in doc.pages():
                text = page.get_text()
                pages_text += f" {text}"

            if not pages_text.strip():
                return "Could not extract text or file is empty.", False

            logger.info(f"Text extracted successfully")
            return pages_text, True

        except Exception as e:
            logger.error(f"Unexpected error during base text extraction: {str(e)}")
            return "", False
