from typing import Optional

from pydantic import BaseModel


class FileResponseSchema(BaseModel):
    filename: str
    content_type: str
    content: Optional[str] = ""


class FileContentExtractionResponse(BaseModel):
    success: bool
    reason: str = ""
    file: Optional[FileResponseSchema] = {}


def builder_file_content_extraction_response(
    success: bool, reason: str = "", filename: str = "", content_type: str = "", content: str = ""
) -> FileContentExtractionResponse:

    file_info = None
    if filename and content_type:
        file_info = FileResponseSchema(filename=filename, content_type=content_type, content=content if success else "")

    return FileContentExtractionResponse(success=success, reason=reason if not success else "", file=file_info)
