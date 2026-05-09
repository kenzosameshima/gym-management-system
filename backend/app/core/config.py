from enum import StrEnum
from functools import lru_cache

from pydantic import Field, PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = Field(min_length=1)
    APP_ENV: AppEnvironment
    DEBUG: bool
    LOG_LEVEL: str = Field(min_length=1)
    SECRET_KEY: str = Field(min_length=32)
    DATABASE_URL: PostgresDsn
    BACKEND_CORS_ORIGINS: str = ""
    DATABASE_POOL_SIZE: int = Field(default=5, ge=1)
    DATABASE_MAX_OVERFLOW: int = Field(default=10, ge=0)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=1)
    JWT_ALGORITHM: str = Field(default="HS256", min_length=1)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.APP_ENV == AppEnvironment.PRODUCTION:
            if self.DEBUG:
                raise ValueError("DEBUG must be false in production.")
            if "*" in self.cors_origins:
                raise ValueError("Wildcard CORS origins are not allowed in production.")
            if self.SECRET_KEY == "local-development-secret-key-change-before-production":
                raise ValueError("SECRET_KEY must be changed in production.")
        return self

    @property
    def cors_origins(self) -> list[str]:
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
