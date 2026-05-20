from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="MyManager AI API", alias="APP_NAME")
    app_env: Literal["development", "test", "staging", "production"] = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, ge=1, le=65535, alias="APP_PORT")
    app_log_level: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = Field(
        default="INFO", alias="APP_LOG_LEVEL"
    )

    database_url: str = Field(default="sqlite:///./tracker.db", min_length=1, alias="DATABASE_URL")

    jwt_secret_key: SecretStr = Field(default=SecretStr("change-me"), alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1, le=1440, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    reminder_worker_enabled: bool = Field(default=True, alias="REMINDER_WORKER_ENABLED")
    reminder_worker_interval_seconds: int = Field(default=60, ge=5, le=86400, alias="REMINDER_WORKER_INTERVAL_SECONDS")
    reminder_worker_retry_attempts: int = Field(default=3, ge=0, le=10, alias="REMINDER_WORKER_RETRY_ATTEMPTS")
    reminder_worker_retry_backoff_seconds: int = Field(
        default=5, ge=1, le=3600, alias="REMINDER_WORKER_RETRY_BACKOFF_SECONDS"
    )

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        insecure_defaults = {"change-me", "change-me-in-production", "change-me-in-development-only"}
        secret_value = self.jwt_secret_key.get_secret_value()
        if self.app_env != "development" and secret_value in insecure_defaults:
            raise ValueError("JWT_SECRET_KEY must be explicitly set to a strong secret outside development.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
