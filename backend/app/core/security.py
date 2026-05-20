"""Security utilities (API key validation, input sanitization)."""

import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a random API key for optional client auth."""
    return secrets.token_urlsafe(32)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional API key verification.
    If API_KEY is not set in env, all requests are allowed.
    """
    settings = get_settings()
    expected = getattr(settings, "API_KEY", None)
    if not expected:
        return api_key
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return api_key
