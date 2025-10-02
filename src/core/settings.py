from pydantic_settings import BaseSettings
from decouple import config


class _AWSSettings(BaseSettings):
    AWS_ACCESS_KEY_ID: str = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = config("AWS_SECRET_ACCESS_KEY")


class _AWSS3Settings(_AWSSettings):
    S3_BUCKET_NAME: str = config("S3_BUCKET_NAME")
    AWS_REGION: str = config("AWS_REGION")


class _AWSBedrockSettings(_AWSSettings):
    AWS_BEDROCK_REGION: str = config("AWS_BEDROCK_REGION", "")


class _AzureOCRSettings(BaseSettings):
    AZURE_OCR_ENDPOINT: str = config("AZURE_OCR_ENDPOINT")
    AZURE_OCR_SECRET_KEY: str = config("AZURE_OCR_SECRET_KEY")


class _AppSettings(_AWSS3Settings, _AWSBedrockSettings, _AzureOCRSettings): ...


settings = _AppSettings()
