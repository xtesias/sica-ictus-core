"""Application configuration loaded from environment variables.

Pydantic Settings reads from .env files (in dev) or actual environment
variables (in containers and production). All config flows through this
module so the rest of the app never reads os.environ directly.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Field names are case-insensitive when matched to environment variables.
    SINGLE_USER_MODE in the environment maps to single_user_mode here.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ----------------------------------------------------------------------
    # Application
    # ----------------------------------------------------------------------
    app_name: str = "sica-ictus-api"
    app_version: str = "0.1.0"
    environment: Literal["development", "production", "test"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # ----------------------------------------------------------------------
    # Database — used in PLAT-8, configured now
    # ----------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://sica-ictus:sica-ictus-dev@postgres:5432/sica-ictus",
        description="Async Postgres URL. Use 'postgres' as host inside docker-compose.",
    )
    database_url_local: str = Field(
        default="postgresql+asyncpg://sica-ictus:sica-ictus-dev@localhost:5432/sica-ictus",
        description="Async Postgres URL for running outside docker-compose (e.g. alembic).",
    )

    # ----------------------------------------------------------------------
    # Redis — used in PLAT-9, configured now
    # ----------------------------------------------------------------------
    redis_url: str = Field(
        default="redis://redis:6379",
        description="Redis URL. Use 'redis' as host inside docker-compose.",
    )
    redis_url_local: str = Field(
        default="redis://localhost:6379",
        description="Redis URL for running outside docker-compose.",
    )

    # ----------------------------------------------------------------------
    # Auth — used in PLAT-8, configured now
    # ----------------------------------------------------------------------
    single_user_mode: bool = Field(
        default=True,
        description="When True, /me returns the default user without JWT validation.",
    )
    jwt_secret: str = Field(
        default="",
        description="JWT signing secret. Must be set in non-development environments.",
    )
    auth_secret: str = Field(
        default="",
        description="Auth.js (frontend) secret. Must be set in non-development environments.",
    )

    # ----------------------------------------------------------------------
    # CORS
    # ----------------------------------------------------------------------
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins for the frontend.",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance.

    Using lru_cache means the .env file is parsed once per process.
    Override via the dependency override mechanism in tests.
    """
    return Settings()