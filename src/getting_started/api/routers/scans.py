"""Scans router for triggering and listing scans."""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from getting_started.api.deps import get_backend, require_api_key
from getting_started.api.schemas import ScanRequest
from getting_started.guardrails import scan_directory

LOG = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])


def _run_scan_job(scan_dir: str, job_id: str, backend) -> None:
    """Run a scan job in the background.

    Args:
        scan_dir: Directory to scan.
        job_id: The batch job ID.
        backend: The storage backend.
    """
    try:
        from getting_started.integrations.events import publish_scan_event
        from getting_started.integrations.webhooks import (
            fire_webhook,
            get_webhook_event_payload,
        )

        backend.update_batch_job_status(job_id, "running")
        result = scan_directory(Path(scan_dir))
        backend.store_findings(result)

        result_data = {
            "scan_directory": result.scan_directory,
            "total_findings": result.total_findings,
        }
        backend.update_batch_job_status(job_id, "completed", result_data)

        LOG.info(
            "Scan job %s completed with %d findings", job_id, result.total_findings
        )

        publish_scan_event(result.scan_directory, result.total_findings)

        webhooks = backend.get_webhook_subscriptions()
        for webhook in webhooks:
            if (
                "*" not in webhook["event_types"]
                and "scan.completed" not in webhook["event_types"]
            ):
                continue
            payload = get_webhook_event_payload(
                "guardrails.scan.completed",
                result_data,
            )
            import asyncio

            asyncio.run(
                fire_webhook(
                    webhook["url"],
                    payload,
                    webhook.get("hmac_secret"),
                )
            )

    except Exception as e:
        LOG.error("Scan job %s failed: %s", job_id, e)
        backend.update_batch_job_status(job_id, "failed", {"error": str(e)})


@router.post("", response_model=dict)
async def trigger_scan(
    request: Request,
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Trigger a new scan.

    Args:
        request: FastAPI request.
        scan_request: Scan parameters.
        background_tasks: FastAPI background tasks.
        api_key: Validated API key.

    Returns:
        Scan job details.
    """
    backend = get_backend(request)
    job_id = backend.create_batch_job(scan_request.path)
    background_tasks.add_task(_run_scan_job, scan_request.path, job_id, backend)
    LOG.info("Triggered scan job %s for path %s", job_id, scan_request.path)
    return {"job_id": job_id, "status": "queued", "path": scan_request.path}


@router.get("/{job_id}")
async def get_scan_status(
    request: Request,
    job_id: str,
    api_key: Annotated[str, Depends(require_api_key)],
) -> dict:
    """Get the status of a scan job.

    Args:
        request: FastAPI request.
        job_id: The batch job ID.
        api_key: Validated API key.

    Returns:
        Job status and results.

    Raises:
        HTTPException: If job not found.
    """
    backend = get_backend(request)
    job = backend.get_batch_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan job '{job_id}' not found",
        )
    LOG.info("Retrieved status for scan job %s", job_id)
    return dict(job)
