"""
Redis cache-aside layer for KV store operations.

Provides cache_get/cache_set/cache_delete functions with automatic
fallback if Redis is unreachable.
"""

import logging
import os
from typing import Optional

import redis

LOG = logging.getLogger(__name__)

KV_CACHE_TTL_SECONDS = int(os.environ.get("KV_CACHE_TTL_SECONDS", "300"))
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get or create a Redis client.

    Returns None if Redis is unavailable (logs a warning and continues).
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        LOG.info("Connected to Redis at %s", REDIS_URL)
        return _redis_client
    except Exception as e:
        LOG.warning(
            "Could not connect to Redis at %s: %s. Caching disabled.",
            REDIS_URL,
            e,
        )
        return None


def cache_get(key: str) -> Optional[str]:
    """Get a value from cache.

    Args:
        key: Cache key.

    Returns:
        Cached value if found, None if not found or Redis unavailable.
    """
    client = get_redis_client()
    if client is None:
        return None

    try:
        return client.get(key)
    except Exception as e:
        LOG.warning("Cache get failed for key %s: %s", key, e)
        return None


def cache_set(key: str, value: str, ttl: int = KV_CACHE_TTL_SECONDS) -> None:
    """Set a value in cache.

    Args:
        key: Cache key.
        value: Value to cache.
        ttl: Time-to-live in seconds.
    """
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, ttl, value)
        LOG.debug("Cached key %s with TTL %d", key, ttl)
    except Exception as e:
        LOG.warning("Cache set failed for key %s: %s", key, e)


def cache_delete(key: str) -> None:
    """Delete a value from cache.

    Args:
        key: Cache key.
    """
    client = get_redis_client()
    if client is None:
        return

    try:
        client.delete(key)
        LOG.debug("Deleted cached key %s", key)
    except Exception as e:
        LOG.warning("Cache delete failed for key %s: %s", key, e)
