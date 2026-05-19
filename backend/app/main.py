from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger, request_id_ctx_var
from app.services.reminder_worker import worker

configure_logging(settings.app_log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.reminder_worker_enabled:
        worker.interval_seconds = settings.reminder_worker_interval_seconds
        worker.retry_attempts = settings.reminder_worker_retry_attempts
        worker.retry_backoff_seconds = settings.reminder_worker_retry_backoff_seconds
        worker.start()
    try:
        yield
    finally:
        if settings.reminder_worker_enabled:
            worker.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def bind_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid4())
    token = request_id_ctx_var.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_ctx_var.reset(token)
    response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
