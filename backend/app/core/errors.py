class AppError(Exception):
    def __init__(self, detail: str, *, status_code: int = 400, code: str = "app_error") -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.code = code


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found", *, code: str = "not_found") -> None:
        super().__init__(detail, status_code=404, code=code)


class ConflictError(AppError):
    def __init__(self, detail: str = "Conflict", *, code: str = "conflict") -> None:
        super().__init__(detail, status_code=409, code=code)


class ValidationError(AppError):
    def __init__(self, detail: str = "Validation failed", *, code: str = "validation_error") -> None:
        super().__init__(detail, status_code=422, code=code)
