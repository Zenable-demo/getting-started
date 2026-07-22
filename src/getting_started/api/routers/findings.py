"""Findings router for guardrail scan results."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from getting_started.api.deps import get_backend, require_api_key
from getting_started.api.schemas import FindingDecisionRequest, FindingResponse

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/findings", tags=["findings"])


@router.get("", response_model=list[FindingResponse])
async def list_findings(
    request: Request,
    api_key: Annotated[str, Depends(require_api_key)],
    limit: int = 100,
) -> list[FindingResponse]:
    """List all guardrail findings.

    Args:
        request: FastAPI request.
        api_key: Validated API key.
        limit: Maximum findings to return.

    Returns:
        List of findings.
    """
    backend = get_backend(request)
    findings = backend.get_findings(limit=limit)
    LOG.info("Listed %d findings", len(findings))
    return findings


@router.post("/{finding_id}/decision")
async def record_decision(
    request: Request,
    finding_id: str,
    decision: FindingDecisionRequest,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Record a decision on a finding (approve/reject).

    Args:
        request: FastAPI request.
        finding_id: The finding ID.
        decision: The decision details.
        api_key: Validated API key.

    Returns:
        Confirmation message.
    """
    if decision.decision not in ("approve", "reject"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Decision must be 'approve' or 'reject'",
        )

    backend = get_backend(request)
    backend.record_finding_decision(finding_id, decision.decision, "api", decision.note)
    LOG.info("Recorded %s decision for finding %s", decision.decision, finding_id)
    return {
        "status": "recorded",
        "finding_id": finding_id,
        "decision": decision.decision,
    }
