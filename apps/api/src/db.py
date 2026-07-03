"""Database connection setup.

Configures the async SQLAlchemy engine and the declarative Base.
Models are defined in src/models/ and inherit from Base.

Session management (the get_db dependency for routes) is added in PLAT-8.
"""
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy ORM models."""
    pass


def create_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine using settings."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.environment == "development" and settings.log_level == "DEBUG",
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


# Lazily-created module-level engine and session factory.
# The actual engine is created on app startup (see main.py lifespan).
engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker | None = None


def init_db() -> None:
    """Initialize the engine and session factory. Called from app lifespan."""
    global engine, SessionLocal
    engine = create_engine()
    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )


async def close_db() -> None:
    """Dispose of the engine on app shutdown."""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None