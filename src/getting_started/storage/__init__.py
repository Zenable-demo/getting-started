"""
Storage abstraction layer for getting-started.

Provides a backend-agnostic interface for data persistence across
PostgreSQL, SQLite, and other backends.
"""

from getting_started.storage.base import StorageBackend
from getting_started.storage.factory import get_backend

__all__ = ["StorageBackend", "get_backend"]
