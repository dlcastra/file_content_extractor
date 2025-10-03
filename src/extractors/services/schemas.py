import io
from typing import Union, Optional, Any

from pydantic import BaseModel, model_validator


class FileInfoSchema(BaseModel):
    filename: str
    content_type: str
    file_bytes: Union[bytes, io.BytesIO]
    content: Optional[str] = ""

    class Config:
        arbitrary_types_allowed = True


class FileContentExtractSchema(BaseModel):
    success: bool
    http_status: Optional[int] = 200
    reason: Optional[str] = ""
    file: FileInfoSchema

    class Config:
        arbitrary_types_allowed = True


class ProcessedFileSchema(BaseModel):
    processed: bool
    http_status: Optional[int] = 200
    reason: Optional[str] = ""
    text: Optional[str] = ""

    @model_validator(mode="before")
    def check_processed_dependencies(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Validates that 'text' is present if 'processed' is True,
        and 'reason' is present if 'processed' is False.
        """

        processed = values.get("processed")
        text = values.get("text")
        reason = values.get("reason")

        if processed and not text:
            raise ValueError("text field is required when processing is successful")
        if not processed and not reason:
            raise ValueError("reason field is required when processing fails")

        return values
