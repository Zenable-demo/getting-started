"""
Audit log helpers for recording data-changing operations.

Delegates to the storage backend's record_audit_event method.
"""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from getting_started.storage.base import StorageBackend

LOG = logging.getLogger(__name__)


def record_audit_event(
    backend: "StorageBackend",
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[dict] = None,
) -> int:
    """Record an audit event via the backend.

    Args:
        backend: The storage backend.
        actor: Who performed the action.
        action: What was done.
        resource_type: The type of resource affected.
        resource_id: The ID of the affected resource.
        details: Optional extra context.

    Returns:
        The audit event ID.
    """
    return backend.record_audit_event(
        actor, action, resource_type, resource_id, details
    )
