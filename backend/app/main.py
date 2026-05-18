from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging

configure_logging(settings.app_log_level)

app = FastAPI(title=settings.app_name)
register_error_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
