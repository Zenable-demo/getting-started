"""Health check router."""

from fastapi import APIRouter

from getting_started import __version__
from getting_started.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status and version.
    """
    return HealthResponse(status="ok", version=__version__)
