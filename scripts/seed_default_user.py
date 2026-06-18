"""Seed the default user for single-user mode.

Usage:
    uv run python scripts/seed_default_user.py "Your Name" "your@email.com"

This script is idempotent — running it twice updates the existing user
rather than creating a duplicate. The settings.default_user_id is set
on first run and updated on subsequent runs.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the API src to path so we can use its db setup
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


async def seed_user(name: str, email: str) -> None:
    """Create or update the default user and configure settings."""
    db_url = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL or DATABASE_URL_LOCAL must be set")

    engine = create_async_engine(db_url, echo=False)

    async with AsyncSession(engine) as session:
        # Check if user already exists by email
        result = await session.execute(
            text("SELECT id, name FROM users WHERE email = :email"),
            {"email": email},
        )
        existing = result.fetchone()

        if existing:
            user_id = existing[0]
            await session.execute(
                text("UPDATE users SET name = :name WHERE id = :id"),
                {"name": name, "id": user_id},
            )
            print(f"Updated existing user: {name} <{email}> (id={user_id})")
        else:
            result = await session.execute(
                text(
                    "INSERT INTO users (email, name) "
                    "VALUES (:email, :name) RETURNING id"
                ),
                {"email": email, "name": name},
            )
            user_id = result.scalar_one()
            print(f"Created user: {name} <{email}> (id={user_id})")

        # Update settings.default_user_id
        await session.execute(
            text(
                "UPDATE settings SET default_user_id = :user_id, "
                "single_user_mode = true WHERE id = 1"
            ),
            {"user_id": user_id},
        )
        print(f"Set settings.default_user_id = {user_id}")
        print("Set settings.single_user_mode = true")

        await session.commit()

    await engine.dispose()


def main() -> None:
    if len(sys.argv) != 3:
        print('Usage: uv run python scripts/seed_default_user.py "Name" "email"')
        sys.exit(1)

    name, email = sys.argv[1], sys.argv[2]
    asyncio.run(seed_user(name, email))


if __name__ == "__main__":
    main()