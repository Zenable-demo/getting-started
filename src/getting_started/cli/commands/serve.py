"""Serve subcommand: run the REST API server."""

import argparse
import logging

LOG = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    """Run the FastAPI server.

    Args:
        args: Parsed arguments with host and port.

    Returns:
        Exit code (never returns in normal operation, serves indefinitely).
    """
    try:
        import uvicorn

        from getting_started.api.app import create_app

        LOG.info("Starting API server on %s:%d", args.host, args.port)

        app = create_app()
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0
    except ImportError:
        LOG.error(
            "FastAPI or uvicorn not installed. Please install getting-started with all dependencies."
        )
        return 1
    except Exception as e:
        LOG.error("Server failed: %s", e)
        return 1
