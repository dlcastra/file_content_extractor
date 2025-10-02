import io

from loguru import logger

from src.azure.handlers import extract_text_file_bytes


class ProcessorMixin:
    async def _use_base_text_extraction(self, file_bytes: bytes | io.BytesIO) -> tuple[str, bool]:
        raise NotImplementedError("This method should be implemented by subclasses.")

    async def _use_ocr_text_extraction(self, file_bytes: bytes | io.BytesIO) -> tuple[str, bool]:
        """Sends the PDF bytes to Azure OCR for text extraction."""

        try:
            logger.info(f"Starting OCR text extraction from PDF file")

            ocr_extracted_text = await extract_text_file_bytes(file_bytes)
            if ocr_extracted_text and ocr_extracted_text == " ":
                return "Could not extract text via OCR or file is empty.", False

            logger.info(f"OCR text extracted successfully")
            return ocr_extracted_text, True

        except Exception as e:
            logger.error(f"Unexpected error during OCR text extraction: {str(e)}")
            return "", False

    async def _use_combine_extraction_methods(self, file_bytes: bytes | io.BytesIO) -> tuple[str, bool]:
        """Use both base and OCR extraction methods."""
        raise NotImplementedError("This method should be implemented by subclasses.")
