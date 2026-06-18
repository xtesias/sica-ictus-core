"""Alembic environment configuration.

Reads database URL from environment variables.
Uses DATABASE_URL_LOCAL when running from the host (for local migrations).
Falls back to DATABASE_URL when running inside containers.
"""
import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add the API src directory to the path so we can import the models
REPO_ROOT = Path(__file__).resolve().parent.parent
API_SRC = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_SRC))

# Import metadata from the API's SQLAlchemy models
# This import is set up in PLAT-8 when src/models/__init__.py registers all models
# For PLAT-6 we'll import a minimal Base
try:
    from src.db import Base
    target_metadata = Base.metadata
except ImportError:
    # PLAT-6 fallback: import inline from the migration's own base
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass

    target_metadata = Base.metadata

# Alembic config object
config = context.config

# Resolve the database URL from environment
# Prefer DATABASE_URL_LOCAL when running outside Docker
db_url = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError(
        "DATABASE_URL or DATABASE_URL_LOCAL must be set in environment"
    )
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generates SQL without DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Synchronous migration runner used inside the async wrapper."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode — connects to the database."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Wrapper that runs the async migrations from a sync entry point."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()