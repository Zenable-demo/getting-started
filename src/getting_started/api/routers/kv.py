"""Key-value store router."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from getting_started.api.deps import get_backend, require_api_key
from getting_started.api.schemas import KVStoreEntry, KVStoreRequest

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/kv", tags=["kv"])


@router.get("", response_model=list[KVStoreEntry])
async def list_kv_store(
    request: Request,
    api_key: Annotated[str, Depends(require_api_key)],
) -> list[KVStoreEntry]:
    """List all key-value pairs.

    Args:
        request: FastAPI request.
        api_key: Validated API key.

    Returns:
        List of KV entries.
    """
    backend = get_backend(request)
    entries = backend.kv_list()
    LOG.info("Listed %d KV entries", len(entries))
    return entries


@router.get("/{key}", response_model=KVStoreEntry)
async def get_kv_value(
    request: Request,
    key: str,
    api_key: Annotated[str, Depends(require_api_key)],
) -> KVStoreEntry:
    """Get a value by key.

    Args:
        request: FastAPI request.
        key: The key to retrieve.
        api_key: Validated API key.

    Returns:
        The KV entry.

    Raises:
        HTTPException: If key not found.
    """
    backend = get_backend(request)
    value = backend.kv_get(key)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key '{key}' not found",
        )
    LOG.info("Retrieved KV value for key: %s", key)
    return {"key": key, "value": value, "updated_at": None}


@router.post("/{key}")
async def set_kv_value(
    request: Request,
    key: str,
    item: KVStoreRequest,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Set a key-value pair.

    Args:
        request: FastAPI request.
        key: The key to set.
        item: The value to store.
        api_key: Validated API key.

    Returns:
        Confirmation message.
    """
    backend = get_backend(request)
    backend.kv_set(key, item.value)
    LOG.info("Set KV value for key: %s", key)
    return {"status": "set", "key": key}


@router.delete("/{key}")
async def delete_kv_value(
    request: Request,
    key: str,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Delete a key-value pair.

    Args:
        request: FastAPI request.
        key: The key to delete.
        api_key: Validated API key.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: If key not found.
    """
    backend = get_backend(request)
    deleted = backend.kv_delete(key)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key '{key}' not found",
        )
    LOG.info("Deleted KV key: %s", key)
    return {"status": "deleted", "key": key}
