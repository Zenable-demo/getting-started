#!/usr/bin/env python3
"""
getting-started script entrypoint
"""

from getting_started import config
from getting_started.postgres import connect, create_table, get_records, store_record


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
    finally:
        conn.close()
        log.info("Database connection closed")


if __name__ == "__main__":
    main()
