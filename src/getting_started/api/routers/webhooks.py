"""Webhooks router for managing subscriptions."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from getting_started.api.deps import get_backend, require_api_key
from getting_started.api.schemas import WebhookSubscriptionRequest

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.get("")
async def list_webhooks(
    request: Request,
    api_key: Annotated[str, Depends(require_api_key)],
) -> list[dict]:
    """List all webhook subscriptions.

    Args:
        request: FastAPI request.
        api_key: Validated API key.

    Returns:
        List of webhook subscriptions.
    """
    backend = get_backend(request)
    webhooks = backend.get_webhook_subscriptions()
    LOG.info("Listed %d webhooks", len(webhooks))
    return webhooks


@router.post("")
async def create_webhook(
    request: Request,
    webhook: WebhookSubscriptionRequest,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Create a webhook subscription.

    Args:
        request: FastAPI request.
        webhook: Webhook subscription details.
        api_key: Validated API key.

    Returns:
        Created webhook subscription.
    """
    backend = get_backend(request)
    subscription_id = backend.add_webhook_subscription(
        webhook.url, webhook.event_types, webhook.hmac_secret
    )
    LOG.info("Created webhook subscription: %s", subscription_id)
    return {"id": subscription_id, "status": "created", "url": webhook.url}


@router.delete("/{subscription_id}")
async def delete_webhook(
    request: Request,
    subscription_id: str,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Delete a webhook subscription.

    Args:
        request: FastAPI request.
        subscription_id: The webhook subscription ID.
        api_key: Validated API key.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: If subscription not found.
    """
    backend = get_backend(request)
    deleted = backend.delete_webhook_subscription(subscription_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook '{subscription_id}' not found",
        )
    LOG.info("Deleted webhook subscription: %s", subscription_id)
    return {"status": "deleted", "subscription_id": subscription_id}
