from io import BytesIO

from fastapi import APIRouter, UploadFile
from starlette import status

from src.extractors.responses.schemas import builder_file_content_extraction_response
from src.extractors.services import get_file_content_extractor

router = APIRouter()


@router.post("/scrape-file-content", status_code=status.HTTP_201_CREATED)
async def scrape_file_content(
    file: UploadFile,
):
    file_content = await file.read()
    file_bytes = BytesIO(file_content)

    service = get_file_content_extractor()
    result = await service.extract_file_content(file.filename, file_bytes, file.content_type)

    return builder_file_content_extraction_response(
        success=result.success,
        reason=result.reason,
        filename=result.file.filename,
        content_type=result.file.content_type,
        content=result.file.content,
    )
