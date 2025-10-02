import io

from loguru import logger

from src.azure.clients import get_ocr_client


async def extract_text_from_pdf_bytes(file_bytes: bytes | io.BytesIO) -> str:
    """
    Extract text from PDF bytes using Azure OCR.
    This function takes a BytesIO object containing PDF data,
    processes it with Azure's OCR service, and returns the extracted text.

    Parameters:
        file_bytes (bytes | io.BytesIO): BytesIO object to read PDF data from.

    Returns:
        str: Extracted text from the PDF.
    """

    try:
        client = get_ocr_client()

        file_stream = file_bytes
        file_stream.seek(0)

        logger.info("Starting OCR analysis on bytes...")
        poller = client.begin_analyze_document("prebuilt-read", document=file_stream)
        result = poller.result()

        extracted_text = []
        for page in result.pages:
            for line in page.lines:
                extracted_text.append(line.content)

        logger.info("Finished OCR analysis...")
        return " ".join(extracted_text)

    except Exception as e:
        logger.error(f"Error extracting text from PDF bytes: {e}", exc_info=True)
        return ""
