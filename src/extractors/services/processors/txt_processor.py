import asyncio
import io

from loguru import logger

from src.extractors.services.schemas import ProcessedFileSchema


class TXTProcessor:
    async def process_txt_bytes(self, file_bytes: bytes | io.BytesIO) -> ProcessedFileSchema:
        """
        Process a TXT file by extracting its text content.
        This method reads the TXT file bytes and decodes it to a string.
        If the file is empty or cannot be decoded, it returns an appropriate message.

        Parameters:
            file_bytes: bytes or io.BytesIO - The TXT file content in bytes or BytesIO format.

        Returns:
            ProcessedFileSchema - An object containing the extracted text and processing status.

            **Examples:**
                - ProcessedFileSchema(processed=True, http_status=201, text="Extracted text from TXT")
                - ProcessedFileSchema(processed=False, http_status=422, reason="Failed to extract text from the file")
        """

        logger.info("Starting TXT file processing")

        if not file_bytes:
            logger.info("Missed file bytes")
            return ProcessedFileSchema(processed=False, reason="Missed file bytes")

        extracted_file_content, processed = await self._use_base_txt_text_extraction(file_bytes)
        if not processed:
            logger.info("Failed to extract text from the file")
            return ProcessedFileSchema(processed=processed, http_status=422, reason=extracted_file_content)

        return ProcessedFileSchema(processed=processed, http_status=201, text=extracted_file_content)

    async def _use_base_txt_text_extraction(self, file_bytes: bytes | io.BytesIO) -> tuple[str, bool]:
        """
        Extract text from TXT file using standard decoding.
        This method reads the TXT file bytes and decodes it to a string.
        If text extraction is successful, it returns the decoded text.
        If any error occurs during the process, it logs the error and returns an empty string with a failure status.

        Parameters:
            file_bytes: bytes or io.BytesIO - The TXT file content in bytes or BytesIO format.

        Returns:
            tuple[str, bool] - A tuple containing the extracted text (or an empty string if extraction failed)
            and a boolean indicating success (True) or failure (False).

            **Examples:**
                - ("Extracted text from TXT", True)
                - ("", False)
        """

        def _decode() -> str:
            data = file_bytes.getvalue() if isinstance(file_bytes, io.BytesIO) else file_bytes
            return data.decode("utf-8")

        try:
            logger.info(f"Starting text extraction from TXT file")
            text = await asyncio.to_thread(_decode)

            if not text.strip():
                return "Could not extract text or file is empty.", False

            logger.info(f"Text extracted successfully")
            return text, True

        except UnicodeDecodeError as e:
            logger.error(f"Error decoding TXT file: {e}")
            return "Failed to decode the TXT file.", False

        except Exception as e:
            logger.error(f"Unexpected error processing TXT file: {e}")
            return "An unexpected error occurred while processing the TXT file.", False
