import io

from docx import Document
from docx.document import Document as DocumentObject
from loguru import logger

from src.extractors.mixins.processors import ProcessorMixin
from src.extractors.services.schemas import ProcessedFileSchema


class DocxProcessor(ProcessorMixin):
    async def process_docx_bytes(self, file_bytes: bytes | io.BytesIO) -> ProcessedFileSchema:
        """
        Process DOCX file bytes to extract text content.
        Uses base text extraction from python-docx library.

        Parameters:
            file_bytes: bytes or io.BytesIO - The PDF file content in bytes or BytesIO format.

        Returns:
            ProcessedFileSchema - The result of the processing, including success status and extracted text or
            reason for failure. For successful processing requires 'text' field, for failed processing requires 'reason' field.

            **Examples:**
                - ProcessedFileSchema(processed=True, text="Extracted text from PDF")
                - ProcessedFileSchema(processed=False, reason="Failed to extract text from the file")
        """
        logger.info("Starting DOCX file processing")

        if not file_bytes:
            logger.info("Missed file bytes")
            return ProcessedFileSchema(processed=False, reason="Missed file bytes")

        document = Document(file_bytes)
        extracted_file_content, processed = await self._use_base_docx_text_extraction(document)

        if not processed:
            logger.info("Failed to extract text from the file")
            return ProcessedFileSchema(processed=processed, reason="Failed to extract text from the file")

        return ProcessedFileSchema(processed=processed, text=extracted_file_content)

    async def _use_base_docx_text_extraction(self, document: DocumentObject) -> tuple[str, bool]:
        """
        Extract text from DOCX using python-docx library.
        This method reads the DOCX file bytes and extracts text from all paragraphs.
        If text extraction is successful, it returns the concatenated text from all paragraphs.
        If any error occurs during the process, it logs the error and returns an empty string with a failure status.

        Parameters:
            document: DocumentObject - The DOCX document object.

        Returns:
            tuple[str, bool] - A tuple containing the extracted text (or an empty string if extraction failed)
            and a boolean indicating success (True) or failure (False).

            **Examples:**
                - ("Extracted text from DOCX", True)
                - ("", False)
        """

        try:
            logger.info(f"Starting text extraction from DOCX file")

            paragraphs_text = " ".join([para.text for para in document.paragraphs])
            if not paragraphs_text.strip():
                return "Could not extract text or file is empty.", False

            logger.info(f"Text extracted successfully")
            return paragraphs_text, True
        except Exception as e:
            logger.error(f"Error during DOCX text extraction: {e}")
            return "", False

    async def _use_combine_docx_text_extraction(
        self, document: DocumentObject, file_bytes: bytes | io.BytesIO
    ) -> tuple[str, bool]:
        """
        Combine base text extraction and OCR for DOCX files.
        Processed each paragraph step-by-step, if paragraph has text use base extraction, if next paragraph is image use OCR.
        If text extraction is successful, it returns the concatenated text from all paragraphs.
        If any error occurs during the process, it logs the error and returns an empty string with a failure status.

        Parameters:
            document: DocumentObject - The DOCX document object.
            file_bytes: bytes or io.BytesIO - The file content in bytes or BytesIO format.

        Returns:
            tuple[str, bool] - A tuple containing the extracted text (or an empty string if extraction failed)
            and a boolean indicating success (True) or failure (False).

            **Examples:**
                - ("Extracted text from DOCX", True)
                - ("", False)
        """

        raise NotImplementedError("This method is not implemented yet.")
