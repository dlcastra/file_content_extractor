import io

from loguru import logger

from src.extractors.services.docx_processor import DocxProcessor
from src.extractors.services.pdf_processor import ProcessPDFFile
from src.extractors.services.schemas import FileContentExtractSchema, FileInfoSchema
from src.extractors.services.txt_processor import TXTProcessor


class _FileContentExtractor(ProcessPDFFile, DocxProcessor, TXTProcessor):
    def __init__(self):
        self.SUPPORTED_CONTENT_TYPES = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]

    async def extract_file_content(
        self, filename: str, file_bytes: bytes | io.BytesIO, content_type: str
    ) -> FileContentExtractSchema:
        """
        Extract text content from a file based on its type.
        This method automatically determines the file type and applies the appropriate extraction method.

        Parameters:
            filename: str - The name of the file.
            file_bytes: bytes or io.BytesIO - The file content in bytes or BytesIO format.
            content_type: str - The MIME type of the file (e.g., 'application/pdf').

        Returns:
            FileContentExtractSchema - The result of the extraction, including success status, reason for failure
            (if any), and the extracted content.

            **Examples:**
                - FileContentExtractSchema(success=True, reason="", file=FileInfoSchema(...))
                - FileContentExtractSchema(success=False, reason="Unsupported file type", file=FileInfoSchema(...))

            **Example of FileInfoSchema:**
                - FileInfoSchema(filename="document.pdf", content_type="application/pdf", file_bytes=b'...', content="Extracted text from PDF")
        """

        try:
            if not file_bytes:
                logger.info("Missed file bytes")
                return self._build_response(False, "Missed file bytes", filename, file_bytes, content_type)

            elif content_type not in self.SUPPORTED_CONTENT_TYPES:
                logger.info(f"Unsupported content type: {content_type}")
                return self._build_response(False, "Unsupported file type", filename, file_bytes, content_type)

            result, processed = await self._process_file_bytes(file_bytes, content_type)
            return self._build_response(processed, result, filename, file_bytes, content_type)
        except (KeyError, Exception) as e:
            logger.error(str(e))
            return self._build_response(False, str(e), filename, file_bytes, content_type)

    @staticmethod
    def _build_response(
        success: bool, result: str, filename: str, file_bytes: bytes | io.BytesIO, content_type: str
    ) -> FileContentExtractSchema:
        """
        Build the response schema for file content extraction.

        Parameters:
            success: bool - Indicates if the extraction was successful.
            result: str - The extracted content or reason for failure.
            filename: str - The name of the file.
            file_bytes: bytes or io.BytesIO - The file content in bytes or BytesIO format.
            content_type: str - The MIME type of the file.
        """

        return FileContentExtractSchema(
            success=success,
            reason="" if success else result,
            file=FileInfoSchema(
                filename=filename, content_type=content_type, file_bytes=file_bytes, content=result if success else ""
            ),
        )

    async def _process_file_bytes(self, file_bytes: bytes | io.BytesIO, content_type: str) -> tuple[str, bool]:
        """
        Process the file bytes based on the content type.
        This method checks the content type and applies the appropriate processing method.

        Parameters:
            file_bytes: bytes or io.BytesIO - The file content in bytes or BytesIO format.
            content_type: str - The MIME type of the file (e.g., 'application/pdf').

        Returns:
            tuple[str, bool] - A tuple containing the extracted content (or reason for failure)
            and a boolean indicating success (True) or failure (False).

            **Examples:**
                - ("Extracted text from PDF", True)
                - ("Unsupported file type", False)
        """

        try:
            file_bytes.seek(0)
            if "pdf" in content_type:
                processed_pdf = await self.process_pdf_bytes(file_bytes)
                return processed_pdf.text or processed_pdf.reason, processed_pdf.processed

            elif "wordprocessingml.document" in content_type:
                processed_docx = await self.process_docx_bytes(file_bytes)
                return processed_docx.text or processed_docx.reason, processed_docx.processed

            elif "text/plain" in content_type:
                processed_txt = await self.process_txt_bytes(file_bytes)
                return processed_txt.text or processed_txt.reason, processed_txt.processed

            return "", False

        except Exception as e:
            logger.error(f"Unexpected error during file processing: {str(e)}")
            return "Unexpected error during file processing", False


def get_file_content_extractor() -> _FileContentExtractor:
    return _FileContentExtractor()
