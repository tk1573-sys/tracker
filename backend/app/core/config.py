from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Tracker API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")

    database_url: str = Field(default="sqlite:///./tracker.db", alias="DATABASE_URL")

    jwt_secret_key: str = Field(default="change-me", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    reminder_worker_enabled: bool = Field(default=True, alias="REMINDER_WORKER_ENABLED")
    reminder_worker_interval_seconds: int = Field(default=60, alias="REMINDER_WORKER_INTERVAL_SECONDS")

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        insecure_defaults = {"change-me", "change-me-in-production", "change-me-in-development-only"}
        if self.app_env.lower() != "development" and self.jwt_secret_key in insecure_defaults:
            raise ValueError("JWT_SECRET_KEY must be explicitly set to a strong secret outside development.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
