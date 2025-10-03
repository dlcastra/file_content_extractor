import io
from typing import Callable

from loguru import logger

from src.extractors.services.processors import GlobalProcessor
from src.extractors.services.schemas import FileContentExtractSchema, FileInfoSchema, ProcessedFileSchema


class _FileContentExtractor(GlobalProcessor):
    def __init__(self):
        self.PROCESSOR_BY_CONTENT_TYPES: dict[str, Callable] = {
            "application/pdf": self.process_pdf_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": self.process_docx_bytes,
            "text/plain": self.process_txt_bytes,
        }

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
                - FileContentExtractSchema(success=True, http_status=200, reason="", file=FileInfoSchema(...))

            **Example of FileInfoSchema:**
                - FileInfoSchema(filename="doc.pdf", content_type="application/pdf", file_bytes=b'...', content="words")
        """

        try:
            if not file_bytes:
                logger.info("Missed file bytes")
                return self._build_response(
                    success=False,
                    http_status=500,
                    result="Missed file bytes",
                    filename=filename,
                    file_bytes=file_bytes,
                    content_type=content_type,
                )

            elif content_type not in self.PROCESSOR_BY_CONTENT_TYPES:
                logger.info(f"Unsupported content type: {content_type}")
                return self._build_response(
                    success=False,
                    http_status=400,
                    result="Unsupported file type",
                    filename=filename,
                    file_bytes=file_bytes,
                    content_type=content_type,
                )

            result = await self._process_file_bytes(file_bytes, content_type)
            return self._build_response(
                success=result.processed,
                http_status=result.http_status,
                result=result.reason if not result.processed else result.text,
                filename=filename,
                file_bytes=file_bytes,
                content_type=content_type,
            )

        except (KeyError, Exception) as e:
            logger.error(str(e))
            return self._build_response(
                success=False,
                http_status=500,
                result=str(e),
                filename=filename,
                file_bytes=file_bytes,
                content_type=content_type,
            )

    @staticmethod
    def _build_response(
        success: bool,
        result: str,
        filename: str,
        file_bytes: bytes | io.BytesIO,
        content_type: str,
        http_status: int = 200,
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
            http_status=http_status,
            reason="" if success else result,
            file=FileInfoSchema(
                filename=filename, content_type=content_type, file_bytes=file_bytes, content=result if success else ""
            ),
        )

    async def _process_file_bytes(self, file_bytes: bytes | io.BytesIO, content_type: str) -> ProcessedFileSchema:
        """
        Process the file bytes based on the content type.
        This method checks the content type and applies the appropriate processing method.

        Parameters:
            file_bytes: bytes or io.BytesIO - The file content in bytes or BytesIO format.
            content_type: str - The MIME type of the file (e.g., 'application/pdf').

        Returns:


            **Examples:**
                - ("Extracted text from PDF", True)
                - ("Unsupported file type", False)
        """

        try:
            file_bytes.seek(0)

            if self.PROCESSOR_BY_CONTENT_TYPES.get(content_type, None):
                processor = self.PROCESSOR_BY_CONTENT_TYPES[content_type]
                processed_file: ProcessedFileSchema = await processor(file_bytes)

                return processed_file

            return ProcessedFileSchema(processed=False, http_status=400, reason="Unsupported file type")

        except Exception as e:
            logger.error(f"Unexpected error during file processing: {str(e)}")
            return ProcessedFileSchema(
                processed=False, http_status=500, reason="Unexpected error during file processing"
            )


def get_file_content_extractor() -> _FileContentExtractor:
    return _FileContentExtractor()
