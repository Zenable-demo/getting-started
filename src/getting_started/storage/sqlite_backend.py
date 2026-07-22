"""
SQLite storage backend implementation.

Uses stdlib sqlite3 for zero-dependency local development without Docker.
Implements the same interface as PostgresBackend.
"""

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from getting_started.guardrails import ScanResult

LOG = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path.home() / ".getting_started" / "db.sqlite3"


class SQLiteBackend:
    """SQLite backend implementation of StorageBackend."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the backend.

        Args:
            db_path: Path to SQLite DB file. Defaults to ~/.getting_started/db.sqlite3.
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Open a connection to SQLite."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        LOG.info("Connected to SQLite at %s", self.db_path)

    def close(self) -> None:
        """Close the SQLite connection."""
        if self.conn:
            self.conn.close()
            LOG.info("SQLite connection closed")

    def migrate(self) -> None:
        """Apply pending migrations."""
        if not self.conn:
            raise RuntimeError("Backend not connected; call connect() first")

        from getting_started.storage.migrations.runner import run_migrations

        run_migrations(self, "sqlite")

    # Events table operations

    def store_record(
        self, name: str, data: Optional[str] = None, table: str = "events"
    ) -> str:
        """Store an event record."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        record_id = str(uuid.uuid4())
        cur = self.conn.cursor()
        cur.execute(
            f"INSERT INTO {table} (id, name, data, created_at) VALUES (?, ?, ?, ?)",
            (record_id, name, data, datetime.now(timezone.utc)),
        )
        self.conn.commit()
        return record_id

    def get_records(self, table: str = "events", limit: int = 10) -> list[dict]:
        """Retrieve recent records."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cur.fetchall()]

    # Key-value store operations

    def kv_set(self, key: str, value: str) -> None:
        """Set a key-value pair and invalidate cache."""
        from getting_started.storage.cache import cache_delete, cache_set

        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO kv_store (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (key, value, datetime.now(timezone.utc)),
        )
        self.conn.commit()
        cache_delete(key)
        cache_set(key, value)
        self.record_audit_event("system", "kv_set", "kv_store", key)

    def kv_get(self, key: str) -> Optional[str]:
        """Get a key-value pair.

        Uses cache-aside pattern: check cache first, fall back to DB.
        """
        from getting_started.storage.cache import cache_get, cache_set

        if not self.conn:
            raise RuntimeError("Backend not connected")

        cached = cache_get(key)
        if cached is not None:
            LOG.debug("Cache hit for key: %s", key)
            return cached

        cur = self.conn.cursor()
        cur.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
        row = cur.fetchone()
        value = row["value"] if row else None

        if value is not None:
            cache_set(key, value)
            LOG.debug("Cached value for key: %s", key)

        return value

    def kv_delete(self, key: str) -> bool:
        """Delete a key-value pair and invalidate cache."""
        from getting_started.storage.cache import cache_delete

        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute("DELETE FROM kv_store WHERE key = ?", (key,))
        self.conn.commit()
        result = cur.rowcount > 0
        if result:
            cache_delete(key)
            self.record_audit_event("system", "kv_delete", "kv_store", key)
        return result

    def kv_list(self) -> list[dict]:
        """List all key-value pairs."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute("SELECT key, value, updated_at FROM kv_store ORDER BY key")
        return [dict(row) for row in cur.fetchall()]

    # Guardrail findings operations

    def store_findings(self, result: ScanResult) -> int:
        """Store scan findings."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        if not result.findings:
            LOG.info("No findings to store")
            return 0

        cur = self.conn.cursor()
        for finding in result.findings:
            cur.execute(
                """
                INSERT INTO guardrail_findings (id, file_path, line_number, pattern_name, line_content, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
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

        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM guardrail_findings ORDER BY scanned_at DESC LIMIT ?",
            (limit,),
        )
        findings = [dict(row) for row in cur.fetchall()]
        LOG.info("Retrieved %d findings", len(findings))
        return findings

    def record_finding_decision(
        self, finding_id: str, decision: str, actor: str, note: Optional[str] = None
    ) -> None:
        """Record a user decision on a finding."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO finding_decisions (id, finding_id, decision, actor, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), finding_id, decision, actor, note),
        )
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
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO audit_log (id, actor, action, resource_type, resource_id, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
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
        return audit_id

    def get_audit_log(self, limit: int = 100) -> list[dict]:
        """Retrieve audit log entries."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM audit_log ORDER BY recorded_at DESC LIMIT ?", (limit,)
        )
        entries = [dict(row) for row in cur.fetchall()]
        LOG.info("Retrieved %d audit log entries", len(entries))
        return entries

    # API key operations

    def verify_api_key(self, raw_key: str) -> Optional[dict]:
        """Verify an API key (stub for now)."""
        return None

    # Batch job operations

    def create_batch_job(self, scan_dir: str) -> str:
        """Create a new batch scan job."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        job_id = str(uuid.uuid4())
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO batch_jobs (id, scan_dir, status) VALUES (?, ?, ?)",
            (job_id, scan_dir, "pending"),
        )
        self.conn.commit()
        LOG.info("Created batch job: id=%s scan_dir=%s", job_id, scan_dir)
        return job_id

    def update_batch_job_status(
        self, job_id: str, status: str, result: Optional[dict] = None
    ) -> None:
        """Update batch job status."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        completed_at = datetime.now(timezone.utc) if status == "completed" else None
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE batch_jobs
            SET status = ?, result = ?, completed_at = ?
            WHERE id = ?
            """,
            (status, json.dumps(result) if result else None, completed_at, job_id),
        )
        self.conn.commit()
        LOG.info("Updated batch job: id=%s status=%s", job_id, status)

    def get_batch_job(self, job_id: str) -> Optional[dict]:
        """Retrieve a batch job by ID."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM batch_jobs WHERE id = ?", (job_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    # Webhook subscriptions

    def add_webhook_subscription(
        self, url: str, event_types: str, hmac_secret: Optional[str] = None
    ) -> str:
        """Add a webhook subscription."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        sub_id = str(uuid.uuid4())
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO webhook_subscriptions (id, url, event_types, hmac_secret)
            VALUES (?, ?, ?, ?)
            """,
            (sub_id, url, event_types, hmac_secret),
        )
        self.conn.commit()
        LOG.info("Added webhook subscription: id=%s url=%s", sub_id, url)
        return sub_id

    def get_webhook_subscriptions(self) -> list[dict]:
        """Retrieve active webhook subscriptions."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM webhook_subscriptions WHERE active = 1")
        subs = [dict(row) for row in cur.fetchall()]
        LOG.info("Retrieved %d webhook subscriptions", len(subs))
        return subs

    def delete_webhook_subscription(self, subscription_id: str) -> bool:
        """Delete a webhook subscription."""
        if not self.conn:
            raise RuntimeError("Backend not connected")

        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM webhook_subscriptions WHERE id = ?", (subscription_id,)
        )
        self.conn.commit()
        result = cur.rowcount > 0
        if result:
            LOG.info("Deleted webhook subscription: id=%s", subscription_id)
        return result
