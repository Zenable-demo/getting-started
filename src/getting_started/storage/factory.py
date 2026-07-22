"""
Storage backend factory for instantiating the appropriate backend.

Reads STORAGE_BACKEND environment variable to select between Postgres and SQLite.
"""

import logging
import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from getting_started.storage.base import StorageBackend

LOG = logging.getLogger(__name__)


def get_backend(backend_kind: Optional[str] = None) -> "StorageBackend":
    """Get an initialized storage backend.

    Args:
        backend_kind: "postgres" or "sqlite". Defaults to STORAGE_BACKEND env var,
                     or "postgres" if not set.

    Returns:
        An instantiated StorageBackend (not yet connected).

    Raises:
        ValueError: If backend_kind is unknown.
    """
    if backend_kind is None:
        backend_kind = os.environ.get("STORAGE_BACKEND", "postgres").lower()

    LOG.info("Creating backend: %s", backend_kind)

    if backend_kind == "postgres":
        from getting_started.storage.postgres_backend import PostgresBackend

        return PostgresBackend()
    elif backend_kind == "sqlite":
        from getting_started.storage.sqlite_backend import SQLiteBackend

        return SQLiteBackend()
    else:
        raise ValueError(
            f"Unknown backend: {backend_kind}. Must be 'postgres' or 'sqlite'."
        )
