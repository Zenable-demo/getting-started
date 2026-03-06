#!/usr/bin/env python3
"""
getting-started script entrypoint
"""

from pathlib import Path

from getting_started import config
from getting_started.guardrails import (
    create_guardrail_table,
    scan_directory,
    store_findings,
)
from getting_started.postgres import (
    connect,
    create_kv_table,
    create_table,
    get_records,
    kv_get,
    kv_list,
    kv_set,
    store_record,
)


def main():
    """Main entry point for the application."""
    log = config.setup_logging()
    log.debug("Logging initialized with level: %s", log.level)

    conn = connect()
    try:
        create_table(conn)
        store_record(conn, name="startup", data="Application started successfully")
        records = get_records(conn)
        for record in records:
            log.info(
                "Record: id=%s name=%s created_at=%s",
                record["id"],
                record["name"],
                record["created_at"],
            )

        # Store application metadata in KV store
        create_kv_table(conn)
        kv_set(conn, "app.version", "0.1.0")
        kv_set(conn, "app.name", "getting-started")
        version = kv_get(conn, "app.version")
        log.info("App version from KV store: %s", version)
        all_kv = kv_list(conn)
        for entry in all_kv:
            log.info("KV: %s = %s", entry["key"], entry["value"])

        # Run guardrails scan
        scan_dir = Path(config.get_scan_dir())
        create_guardrail_table(conn)
        result = scan_directory(scan_dir)
        stored_count = store_findings(conn, result)
        log.info("Guardrails scan complete: %d findings stored", stored_count)

        summary = result.summary_by_pattern()
        for pattern_name, count in summary.items():
            log.info("  %s: %d finding(s)", pattern_name, count)
    finally:
        conn.close()
        log.info("Database connection closed")


if __name__ == "__main__":
    main()
