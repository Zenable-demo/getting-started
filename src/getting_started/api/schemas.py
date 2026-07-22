"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FindingResponse(BaseModel):
    """A guardrail finding."""

    id: str
    file_path: str
    line_number: int
    pattern_name: str
    line_content: str
    scanned_at: datetime


class ScanRequest(BaseModel):
    """Request to start a new scan."""

    path: str = Field(default=".", description="Directory to scan")


class ScanResponse(BaseModel):
    """Response with scan results."""

    scan_dir: str
    total_findings: int
    findings: list[FindingResponse]
    scanned_at: datetime


class KVStoreEntry(BaseModel):
    """A key-value store entry."""

    key: str
    value: str
    updated_at: datetime


class KVStoreRequest(BaseModel):
    """Request to set/update a KV entry."""

    value: str = Field(description="The value to store")


class WebhookSubscription(BaseModel):
    """A webhook subscription."""

    id: str
    url: str
    event_types: str
    active: bool
    created_at: datetime


class WebhookSubscriptionRequest(BaseModel):
    """Request to create a webhook subscription."""

    url: str = Field(description="Webhook URL")
    event_types: str = Field(
        default="*",
        description="Comma-separated event types (e.g., 'scan.completed,kv.updated')",
    )
    hmac_secret: Optional[str] = Field(
        default=None, description="Optional HMAC secret for signing"
    )


class FindingDecisionRequest(BaseModel):
    """Request to record a finding decision."""

    decision: str = Field(description="Decision: 'approve' or 'reject'")
    note: Optional[str] = Field(default=None, description="Optional decision note")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
