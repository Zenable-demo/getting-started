"""
PostgreSQL storage backend implementation.

Delegates to the existing postgres.py for events/KV store operations
(zero duplication) and owns new SQL for findings/audit/api-keys/webhooks.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import psycopg

from getting_started import postgres
from getting_started.guardrails import ScanResult

LOG = logging.getLogger(__name__)


class PostgresBackend:
    """PostgreSQL backend implementation of StorageBackend."""

    def __init__(self):
        """Initialize the backend."""
        self.conn: Optional[psycopg.Connection] = None

    def connect(self) -> None:
        """Open a connection to PostgreSQL."""
        self.conn = postgres.connect()

    def close(self) -> None:
        """Close the PostgreSQL connection."""
        if self.conn:
            self.conn.close()
            LOG.info("PostgreSQL connection closed")

    def migrate(self) -> None:
        """Apply pending migrations."""
        if not self.conn:
            raise RuntimeError("Backend not connected; call connect() first")

        from getting_started.storage.migrations.runner import run_migrations

        run_migrations(self, "postgres")

    # Events table operations (delegated to postgres.py)

    def store_record(
        self, name: str, data: Optional[str] = None, table: str = "events"
    ) -> str:
        """Store an event record."""
        if not self.conn:
            raise RuntimeError("Backend not connected")
        record_id = postgres.store_record(self.conn, name=name, data=data, table=table)
        return str(record_id)

    def get_records(self, table: str = "events", limit: int = 10) -> list[dict]:
        """Retrieve recent records."""
        if not self.conn:
            raise RuntimeError("Backend not connected")
        return postgres.get_records(self.conn, table=table, limit=limit)

    # Key-value store operations (delegated to postgres.py)

    def kv_set(self, key: str, value: str) -> None:
        """Set a key-value pair and invalidate cache."""
        from getting_started.storage.cache import cache_delete, cache_set

        if not self.conn:
            raise RuntimeError("Backend not connected")
        postgres.kv_set(self.conn, key=key, value=value)
        cache_delete(key)
        cache_set(key, value)
        self.record_audit_event("system", "kv_set", "kv_store", key)

    def kv_get(self, key: str) -> Optional[str]:
        """Get a key-value pair using cache-aside pattern."""
        from getting_started.storage.cache import cache_get, cache_set

        if not self.conn:
            raise RuntimeError("Backend not connected")

        cached = cache_get(key)
        if cached is not None:
            LOG.debug("Cache hit for key: %s", key)
            return cached

        value = postgres.kv_get(self.conn, key=key)
        if value is not None:
            cache_set(key, value)
            LOG.debug("Cached value for key: %s", key)

        return value

    def kv_delete(self, key: str) -> bool:
        """Delete a key-value pair and invalidate cache."""
        from getting_started.storage.cache import cache_delete

        if not self.conn:
            raise RuntimeError("Backend not connected")
        result = postgres.kv_delete(self.conn, key=key)
        if result:
            cache_delete(key)
            self.record_audit_event("system", "kv_delete", "kv_store", key)
        return result

    def kv_list(self) -> list[dict]:
        """List all key-value pairs."""
        if not self.conn:
            raise RuntimeError("Backend not connected")
        return postgres.kv_list(self.conn)

    # Guardrail findings operations

    def store_findings(self, result: ScanResult) -> int:
        """Store scan findings."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        if not result.findings:
            LOG.info("No findings to store")
            return 0

        postgres.create_guardrail_table(self.conn)

        query = """
        INSERT INTO guardrail_findings (id, file_path, line_number, pattern_name, line_content, scanned_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            for finding in result.findings:
                cur.execute(
                    query,
                    (
                        str(uuid.uuid4()),
                        finding.file_path,
                        finding.line_number,
                        finding.pattern_name,
                        finding.line_content,
                        result.scanned_at,
                    ),
                )
        self.conn.commit()
        LOG.info("Stored %d guardrail findings", len(result.findings))
        self.record_audit_event(
            "system",
            "store_findings",
            "guardrail_findings",
            result.scan_directory,
            {"count": len(result.findings)},
        )
        return len(result.findings)

    def get_findings(
        self, scan_id: Optional[int] = None, limit: int = 100
    ) -> list[dict]:
        """Retrieve guardrail findings."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = "SELECT * FROM guardrail_findings ORDER BY scanned_at DESC LIMIT %s"
        with self.conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(query, (limit,))
            findings = cur.fetchall()
        LOG.info("Retrieved %d findings", len(findings))
        return findings

    def record_finding_decision(
        self, finding_id: str, decision: str, actor: str, note: Optional[str] = None
    ) -> None:
        """Record a user decision on a finding."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = """
        INSERT INTO finding_decisions (id, finding_id, decision, actor, note)
        VALUES (%s, %s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (str(uuid.uuid4()), finding_id, decision, actor, note))
        self.conn.commit()
        LOG.info(
            "Recorded finding decision: finding_id=%s decision=%s actor=%s",
            finding_id,
            decision,
            actor,
        )
        self.record_audit_event(
            actor, f"finding_{decision}", "finding", finding_id, {"note": note}
        )

    # Audit log operations

    def record_audit_event(
        self,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[dict] = None,
    ) -> str:
        """Record an audit event."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        audit_id = str(uuid.uuid4())
        query = """
        INSERT INTO audit_log (id, actor, action, resource_type, resource_id, details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (
                    audit_id,
                    actor,
                    action,
                    resource_type,
                    resource_id,
                    json.dumps(details) if details else None,
                ),
            )
        self.conn.commit()
        LOG.debug(
            "Recorded audit event: id=%s actor=%s action=%s resource=%s/%s",
            audit_id,
            actor,
            action,
            resource_type,
            resource_id,
        )
        return audit_id

    def get_audit_log(self, limit: int = 100) -> list[dict]:
        """Retrieve audit log entries."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = "SELECT * FROM audit_log ORDER BY recorded_at DESC LIMIT %s"
        with self.conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(query, (limit,))
            entries = cur.fetchall()
        LOG.info("Retrieved %d audit log entries", len(entries))
        return entries

    # API key operations

    def verify_api_key(self, raw_key: str) -> Optional[dict]:
        """Verify an API key (stub for now, extended in DB-backed mode)."""
        return None

    # Batch job operations

    def create_batch_job(self, scan_dir: str) -> str:
        """Create a new batch scan job."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        job_id = str(uuid.uuid4())
        query = """
        INSERT INTO batch_jobs (id, scan_dir, status)
        VALUES (%s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (job_id, scan_dir, "pending"))
        self.conn.commit()
        LOG.info("Created batch job: id=%s scan_dir=%s", job_id, scan_dir)
        return job_id

    def update_batch_job_status(
        self, job_id: str, status: str, result: Optional[dict] = None
    ) -> None:
        """Update batch job status."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = """
        UPDATE batch_jobs
        SET status = %s, result = %s, completed_at = %s
        WHERE id = %s
        """
        completed_at = datetime.now(timezone.utc) if status == "completed" else None
        with self.conn.cursor() as cur:
            cur.execute(
                query,
                (status, json.dumps(result) if result else None, completed_at, job_id),
            )
        self.conn.commit()
        LOG.info("Updated batch job: id=%s status=%s", job_id, status)

    def get_batch_job(self, job_id: str) -> Optional[dict]:
        """Retrieve a batch job by ID."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = "SELECT * FROM batch_jobs WHERE id = %s"
        with self.conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(query, (job_id,))
            job = cur.fetchone()
        return job

    # Webhook subscriptions

    def add_webhook_subscription(
        self, url: str, event_types: str, hmac_secret: Optional[str] = None
    ) -> str:
        """Add a webhook subscription."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        sub_id = str(uuid.uuid4())
        query = """
        INSERT INTO webhook_subscriptions (id, url, event_types, hmac_secret)
        VALUES (%s, %s, %s, %s)
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (sub_id, url, event_types, hmac_secret))
        self.conn.commit()
        LOG.info("Added webhook subscription: id=%s url=%s", sub_id, url)
        return sub_id

    def get_webhook_subscriptions(self) -> list[dict]:
        """Retrieve active webhook subscriptions."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = "SELECT * FROM webhook_subscriptions WHERE active = true"
        with self.conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(query)
            subs = cur.fetchall()
        LOG.info("Retrieved %d webhook subscriptions", len(subs))
        return subs

    def delete_webhook_subscription(self, subscription_id: str) -> bool:
        """Delete a webhook subscription."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        query = "DELETE FROM webhook_subscriptions WHERE id = %s"
        with self.conn.cursor() as cur:
            cur.execute(query, (subscription_id,))
            deleted = cur.rowcount > 0
        self.conn.commit()
        if deleted:
            LOG.info("Deleted webhook subscription: id=%s", subscription_id)
        return deleted
