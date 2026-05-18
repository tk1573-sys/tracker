from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class AppError(Exception):
    def __init__(self, detail: str, status_code: int = 400) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404)


class ConflictError(AppError):
    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail=detail, status_code=409)


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(detail=detail, status_code=401)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(SQLAlchemyError)
    async def db_error_handler(_: Request, __: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "Database operation failed"})
