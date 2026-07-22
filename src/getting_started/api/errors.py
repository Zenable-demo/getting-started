"""
API error handlers and exception classes.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class APIError(Exception):
    """Base API exception."""

    def __init__(self, message: str, status_code: int = 400):
        """Initialize the error.

        Args:
            message: Error message.
            status_code: HTTP status code.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str):
        """Initialize the error."""
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(APIError):
    """Input validation error."""

    def __init__(self, message: str):
        """Initialize the error."""
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


def register_error_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI app.

    Args:
        app: The FastAPI application.
    """

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle API errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": str(exc)},
        )
