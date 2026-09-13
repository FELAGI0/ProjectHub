"""Application settings."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables and an optional .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ProjectHub"
    debug: bool = False
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    api_v1_prefix: str = "/api/v1"
    postgres_db: str = "projecthub"
    postgres_user: str = "projecthub"
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, gt=0, le=65535)
    postgres_ssl: bool = False
    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=15, gt=0)
    jwt_refresh_token_expire_days: int = Field(default=7, gt=0)
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3005",
    ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""

    return Settings()  # type: ignore[call-arg]
