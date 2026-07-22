"""
Abstract storage backend interface as a Protocol.

All storage implementations (Postgres, SQLite, etc.) must conform to this
interface to be interchangeable.
"""

from typing import Optional, Protocol, runtime_checkable

from getting_started.guardrails import ScanResult


@runtime_checkable
class StorageBackend(Protocol):
    """Backend-agnostic storage interface.

    Implementations must support all methods. Storage backends handle all
    data persistence: events, key-value store, guardrail findings, audit logs,
    API keys, webhooks, finding decisions, and batch jobs.
    """

    def connect(self) -> None:
        """Open a connection to the storage backend.

        Raises:
            psycopg.OperationalError: On connection failure (PostgreSQL).
            sqlite3.OperationalError: On connection failure (SQLite).
        """
        ...

    def close(self) -> None:
        """Close the storage connection."""
        ...

    def migrate(self) -> None:
        """Apply pending migrations to the database schema.

        Idempotent: safe to call multiple times.
        """
        ...

    # Events table operations
    def store_record(
        self, name: str, data: Optional[str] = None, table: str = "events"
    ) -> str:
        """Store an event record.

        Args:
            name: Name for the event record.
            data: Optional text data to store.
            table: Target table name.

        Returns:
            The UUID of the inserted record.
        """
        ...

    def get_records(self, table: str = "events", limit: int = 10) -> list[dict]:
        """Retrieve recent records from the events table.

        Args:
            table: Source table name.
            limit: Maximum number of records to return.

        Returns:
            A list of record dictionaries.
        """
        ...

    # Key-value store operations
    def kv_set(self, key: str, value: str) -> None:
        """Set a key-value pair, inserting or updating as needed.

        Args:
            key: The key to store.
            value: The value to associate with the key.
        """
        ...

    def kv_get(self, key: str) -> Optional[str]:
        """Get the value for a key.

        Args:
            key: The key to look up.

        Returns:
            The value if found, or None.
        """
        ...

    def kv_delete(self, key: str) -> bool:
        """Delete a key-value pair.

        Args:
            key: The key to delete.

        Returns:
            True if the key was deleted, False if it did not exist.
        """
        ...

    def kv_list(self) -> list[dict]:
        """List all key-value pairs.

        Returns:
            A list of dictionaries with key, value, and updated_at fields.
        """
        ...

    # Guardrail findings operations
    def store_findings(self, result: ScanResult) -> int:
        """Store scan findings in the database.

        Args:
            result: The scan result containing findings to store.

        Returns:
            The number of findings stored.
        """
        ...

    def get_findings(
        self, scan_id: Optional[int] = None, limit: int = 100
    ) -> list[dict]:
        """Retrieve guardrail findings.

        Args:
            scan_id: Optional scan ID to filter by. If None, returns all.
            limit: Maximum number of findings to return.

        Returns:
            A list of finding dictionaries.
        """
        ...

    def record_finding_decision(
        self, finding_id: str, decision: str, actor: str, note: Optional[str] = None
    ) -> None:
        """Record a user decision (approve/reject) on a finding.

        Args:
            finding_id: The finding UUID.
            decision: "approve" or "reject".
            actor: Who made the decision (CLI user, API key, etc.).
            note: Optional decision note.
        """
        ...

    # Audit log operations
    def record_audit_event(
        self,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[dict] = None,
    ) -> str:
        """Record an audit event for a data-changing operation.

        Args:
            actor: Who performed the action.
            action: What was done (e.g., "kv_set", "finding_approved").
            resource_type: The type of resource affected (e.g., "kv_store", "finding").
            resource_id: The ID of the affected resource.
            details: Optional JSON-serializable extra context.

        Returns:
            The audit event UUID.
        """
        ...

    def get_audit_log(self, limit: int = 100) -> list[dict]:
        """Retrieve audit log entries.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            A list of audit log dictionaries.
        """
        ...

    # API key operations
    def verify_api_key(self, raw_key: str) -> Optional[dict]:
        """Verify an API key and return its metadata if valid.

        Args:
            raw_key: The raw API key from the request header.

        Returns:
            A dict with key metadata if valid, None if invalid or not found.
        """
        ...

    # Batch job operations
    def create_batch_job(self, scan_dir: str) -> str:
        """Create a new batch scan job record.

        Args:
            scan_dir: Directory to scan.

        Returns:
            The job UUID.
        """
        ...

    def update_batch_job_status(
        self, job_id: str, status: str, result: Optional[dict] = None
    ) -> None:
        """Update the status of a batch job.

        Args:
            job_id: The job UUID.
            status: "pending", "running", "completed", or "failed".
            result: Optional results/summary JSON.
        """
        ...

    def get_batch_job(self, job_id: str) -> Optional[dict]:
        """Retrieve a batch job by ID.

        Args:
            job_id: The job UUID.

        Returns:
            Job dict if found, None otherwise.
        """
        ...

    # Webhook subscriptions
    def add_webhook_subscription(
        self, url: str, event_types: str, hmac_secret: Optional[str] = None
    ) -> str:
        """Register a webhook subscription.

        Args:
            url: Webhook URL.
            event_types: Comma-separated event types to subscribe to.
            hmac_secret: Optional HMAC secret for signing deliveries.

        Returns:
            The subscription UUID.
        """
        ...

    def get_webhook_subscriptions(self) -> list[dict]:
        """Retrieve all active webhook subscriptions.

        Returns:
            List of subscription dicts.
        """
        ...

    def delete_webhook_subscription(self, subscription_id: str) -> bool:
        """Remove a webhook subscription.

        Args:
            subscription_id: The subscription UUID.

        Returns:
            True if deleted, False if not found.
        """
        ...
