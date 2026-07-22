"""
API dependencies: authentication, backend injection, and common validators.
"""

import logging
import os
from typing import Annotated

from fastapi import Header, HTTPException, status

LOG = logging.getLogger(__name__)


async def require_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> str:
    """Validate API key from X-API-Key header.

    Args:
        x_api_key: API key from request header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If API key is missing or invalid.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    expected_key = os.environ.get("API_KEY", "demo-key-12345")
    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return x_api_key


def get_backend(request):
    """Get the storage backend from app state.

    Args:
        request: The FastAPI request object.

    Returns:
        The initialized storage backend.

    Raises:
        HTTPException: If backend is not initialized.
    """
    if not hasattr(request.app.state, "backend"):
        LOG.error("Backend not initialized in app state")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backend not available",
        )
    return request.app.state.backend
