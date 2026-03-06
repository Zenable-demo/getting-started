#!/usr/bin/env python3
"""
getting-started script entrypoint
"""

import os
from pathlib import Path

from getting_started import config
from getting_started.guardrails import (
    create_guardrail_table,
    scan_directory,
    store_findings,
)
from getting_started.postgres import connect, create_table, get_records, store_record


def main():
    """Main entry point for the application."""
    log = config.setup_logging()
    log.debug("Logging initialized with level: %s", log.level)

    customer_id = os.environ.get("CUSTOMER_ID", "")
    if not customer_id:
        log.error("CUSTOMER_ID environment variable must be set")
        raise SystemExit(1)

    conn = connect()
    try:
        create_table(conn)
        store_record(
            conn,
            name="startup",
            customer_id=customer_id,
            data="Application started successfully",
        )
        records = get_records(conn, customer_id=customer_id)
        for record in records:
            log.info(
                "Record: id=%s name=%s created_at=%s",
                record["id"],
                record["name"],
                record["created_at"],
            )

        # Run guardrails scan
        scan_dir = Path(config.get_scan_dir())
        create_guardrail_table(conn)
        result = scan_directory(scan_dir)
        stored_count = store_findings(conn, result, customer_id=customer_id)
        log.info("Guardrails scan complete: %d findings stored", stored_count)

        summary = result.summary_by_pattern()
        for pattern_name, count in summary.items():
            log.info("  %s: %d finding(s)", pattern_name, count)
    finally:
        conn.close()
        log.info("Database connection closed")


if __name__ == "__main__":
    main()
