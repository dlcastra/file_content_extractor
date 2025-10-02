from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.extractors.routers import router as extractor_router

app = FastAPI()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan event handler for the FastAPI application."""
    logger.info(f"Lifespan: starting...")

    yield


api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(extractor_router, tags=["Text Extractor"])
app.include_router(api_v1_router, tags=["v1"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc):
    errors = [{"field": err["loc"][-1], "msg": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )
