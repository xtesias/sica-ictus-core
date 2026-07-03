"""Health check endpoint.

Used by Docker healthchecks, monitoring, and acceptance criteria
verification. Returns 200 OK with version info when the app is running.

Does NOT check database connectivity yet — that comes in PLAT-8 when the
database session dependency is wired up.
"""
from fastapi import APIRouter

from src.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return application health status.

    Returns:
        Dictionary with status and version fields.
    """
    settings = get_settings()
    return {
        "status": "ok2",
        "version": settings.app_version,
    }