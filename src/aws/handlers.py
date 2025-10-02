import asyncio
from concurrent import futures
from io import BytesIO
from typing import Tuple

from botocore.exceptions import BotoCoreError, ClientError
from loguru import logger

from src.aws.clients import s3_client
from src.core.constants import CONTENT_TYPES


def sync_upload_bytes_to_s3(bucket: str, s3_key: str, file_bytes: BytesIO, file_format: str) -> Tuple[str, bool]:
    """
    Uploads a BytesIO object to S3.

    :param bucket: S3 bucket name.
    :param s3_key: Destination file name in S3.
    :param file_bytes: File content in BytesIO.
    :param file_format: Target file format (used for MIME type).
    :return: Tuple (status message, success flag).
    """

    content_type = CONTENT_TYPES.get(file_format, "application/octet-stream")

    try:
        file_bytes.seek(0)
        s3_client.upload_fileobj(file_bytes, bucket, s3_key, ExtraArgs={"ContentType": content_type})
        logger.info(f"File {s3_key} uploaded to S3")
        return "Uploaded", True

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
        return "Error while uploading", False

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "Unexpected error", False


async def upload_bytes_to_s3(bucket: str, s3_key: str, file_bytes: BytesIO, file_format: str) -> Tuple[str, bool]:
    """
    Uploads a BytesIO object to S3.

    :param bucket: S3 bucket name.
    :param s3_key: Destination file name in S3.
    :param file_bytes: File content in BytesIO.
    :param file_format: Target file format (used for MIME type).
    :return: Tuple (status message, success flag).
    """

    loop = asyncio.get_event_loop()
    with futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, sync_upload_bytes_to_s3, bucket, s3_key, file_bytes, file_format)

    return result
