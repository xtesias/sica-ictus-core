"""FastAPI application entrypoint.

Run with:
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

The :app suffix tells uvicorn to import the `app` object from this module.
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.db import close_db, init_db
from src.routes import health

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — startup and shutdown handlers.

    Called by FastAPI on app start (before the first request) and shutdown
    (after the last response). Replaces the older @app.on_event decorators.
    """
    settings = get_settings()
    logger.info(
        "starting_app",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        single_user_mode=settings.single_user_mode,
    )

    # Initialize the database engine (does not yet open connections)
    init_db()
    logger.info("database_engine_initialized")

    yield

    # Shutdown
    logger.info("shutting_down")
    await close_db()
    logger.info("database_engine_disposed")


def create_app() -> FastAPI:
    """Application factory.

    Constructs and configures the FastAPI app. Using a factory pattern
    rather than module-level instantiation makes testing easier (each test
    can create a fresh app with different settings).
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="DeFi bug bounty platform API",
        lifespan=lifespan,
    )

    # CORS — allow the Next.js frontend to call us
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount route routers
    app.include_router(health.router)

    return app


app = create_app()