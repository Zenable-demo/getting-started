"""Webhook delivery with HMAC signing and retry logic."""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Optional

import httpx

LOG = logging.getLogger(__name__)

RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1


def sign_webhook_payload(payload: dict, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload.

    Args:
        payload: The webhook payload.
        secret: The HMAC secret.

    Returns:
        Hex-encoded HMAC signature.
    """
    payload_json = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        secret.encode(),
        payload_json.encode(),
        hashlib.sha256,
    ).hexdigest()
    return signature


async def fire_webhook(
    url: str,
    payload: dict,
    hmac_secret: Optional[str] = None,
) -> bool:
    """Send a webhook with retry logic.

    Args:
        url: Webhook URL.
        payload: Payload to send.
        hmac_secret: Optional HMAC secret for signing.

    Returns:
        True if delivery succeeded, False if all retries failed.
    """
    headers = {
        "Content-Type": "application/json",
    }

    if hmac_secret:
        signature = sign_webhook_payload(payload, hmac_secret)
        headers["X-Signature-256"] = signature

    for attempt in range(RETRY_ATTEMPTS):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code in (200, 201, 202, 204):
                    LOG.info("Webhook delivered to %s (attempt %d)", url, attempt + 1)
                    return True
                else:
                    LOG.warning(
                        "Webhook delivery failed: status %d (attempt %d/%d)",
                        response.status_code,
                        attempt + 1,
                        RETRY_ATTEMPTS,
                    )
        except Exception as e:
            LOG.warning(
                "Webhook delivery error: %s (attempt %d/%d)",
                e,
                attempt + 1,
                RETRY_ATTEMPTS,
            )

        if attempt < RETRY_ATTEMPTS - 1:
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    LOG.error("Webhook delivery failed after %d attempts: %s", RETRY_ATTEMPTS, url)
    return False


def get_webhook_event_payload(
    event_type: str,
    data: dict,
) -> dict:
    """Create a webhook event payload.

    Args:
        event_type: Event type (e.g., 'guardrails.scan.completed').
        data: Event data.

    Returns:
        Webhook event payload.
    """
    return {
        "event": event_type,
        "timestamp": time.time(),
        "data": data,
    }
