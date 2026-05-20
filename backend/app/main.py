from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import configure_logging, get_logger
from app.services.reminder_worker import worker

logger = get_logger(__name__)


def create_app() -> FastAPI:
    configure_logging(settings.app_log_level)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if settings.reminder_worker_enabled:
            worker.interval_seconds = settings.reminder_worker_interval_seconds
            worker.max_retry_attempts = settings.reminder_worker_retry_attempts
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
    async def log_request(request: Request, call_next):
        request_id = uuid4().hex
        start = perf_counter()
        logger.info(
            "request_started",
            extra={"event": "request_started", "request_id": request_id, "method": request.method, "path": request.url.path},
        )
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={"event": "request_failed", "request_id": request_id, "method": request.method, "path": request.url.path},
            )
            raise
        duration_ms = round((perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "app_error",
            extra={"event": "app_error", "status_code": exc.status_code, "error_code": exc.code, "detail": exc.detail},
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, "code": exc.code})

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} is running"}

    return app


app = create_app()
