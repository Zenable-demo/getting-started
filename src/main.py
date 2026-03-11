#!/usr/bin/env python3
"""
getting-started script entrypoint
"""

from pathlib import Path

from getting_started import config
from getting_started.customers import (
    create_customer,
    create_customer_table,
    get_customer,
    list_customers,
    update_customer,
)
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

        # Customer data management
        create_customer_table(conn)
        customer_id = create_customer(
            conn, name="Alice Smith", email="alice@example.com", company="Acme Corp"
        )
        log.info("Created customer id=%d", customer_id)
        create_customer(conn, name="Bob Jones", email="bob@example.com")

        customer = get_customer(conn, customer_id)
        if customer:
            log.info(
                "Customer: id=%s name=%s email=%s",
                customer["id"],
                customer["name"],
                customer["email"],
            )

        update_customer(conn, customer_id, status="inactive")
        customers = list_customers(conn)
        for c in customers:
            log.info(
                "Customer: id=%s name=%s status=%s",
                c["id"],
                c["name"],
                c["status"],
            )
    finally:
        conn.close()
        log.info("Database connection closed")


if __name__ == "__main__":
    main()
