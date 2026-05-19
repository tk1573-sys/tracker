from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.services.reminder_worker import worker

configure_logging(settings.app_log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.reminder_worker_enabled:
        worker.interval_seconds = settings.reminder_worker_interval_seconds
        worker.start()
    try:
        yield
    finally:
        if settings.reminder_worker_enabled:
            worker.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
