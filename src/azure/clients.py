from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from src.core.settings import settings


def get_ocr_client() -> DocumentAnalysisClient:
    return DocumentAnalysisClient(
        endpoint=settings.AZURE_OCR_ENDPOINT,
        credential=AzureKeyCredential(settings.AZURE_OCR_SECRET_KEY),
    )
