"""
FastAPI application factory.

Creates and configures the API app with all routes, middleware,
and lifespan handlers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Handles startup (migrations, connection pools) and shutdown.
    """
    LOG.info("Starting up API server...")
    try:
        from getting_started.storage import get_backend

        backend = get_backend()
        backend.connect()
        backend.migrate()
        app.state.backend = backend
        LOG.info("Backend initialized and migrations applied")
    except Exception as e:
        LOG.error("Failed to initialize backend: %s", e)
        raise

    yield

    LOG.info("Shutting down API server...")
    if hasattr(app.state, "backend"):
        app.state.backend.close()
        LOG.info("Backend connection closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.
    """
    app = FastAPI(
        title="getting-started",
        description="A playground for getting started with Zenable",
        version="0.1.0",
        lifespan=lifespan,
    )

    from getting_started.api import errors
    from getting_started.api.routers import findings, health, kv, scans, webhooks

    errors.register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(findings.router)
    app.include_router(kv.router)
    app.include_router(scans.router)
    app.include_router(webhooks.router)

    LOG.info("API app created with all routers and error handlers")
    return app
