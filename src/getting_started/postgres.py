"""
PostgreSQL database integration for getting-started.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import psycopg
from psycopg.rows import dict_row

LOG = logging.getLogger(__name__)

DEFAULT_TABLE = "events"


def get_connection_string() -> str:
    """Build a PostgreSQL connection string from environment variables.

    Environment variables:
        POSTGRES_HOST: Database host (default: localhost).
        POSTGRES_PORT: Database port (default: 5432).
        POSTGRES_DB: Database name (default: getting_started).
        POSTGRES_USER: Database user (default: postgres).
        POSTGRES_PASSWORD: Database password (default: postgres).

    Returns:
        A PostgreSQL connection string.
    """
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    dbname = os.environ.get("POSTGRES_DB", "getting_started")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


def connect() -> psycopg.Connection:
    """Connect to the PostgreSQL database.

    Returns:
        A psycopg connection object.

    Raises:
        psycopg.OperationalError: If the connection fails.
    """
    conninfo = get_connection_string()
    LOG.info("Connecting to PostgreSQL at %s", conninfo.split("password=")[0])
    conn = psycopg.connect(conninfo, row_factory=dict_row)
    LOG.info("Connected to PostgreSQL successfully")
    return conn


def create_table(conn: psycopg.Connection, table: str = DEFAULT_TABLE) -> None:
    """Create the events table if it does not exist.

    Args:
        conn: An active psycopg connection.
        table: Name of the table to create.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        data TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()
    LOG.info("Table '%s' is ready", table)


def store_record(
    conn: psycopg.Connection,
    name: str,
    data: Optional[str] = None,
    table: str = DEFAULT_TABLE,
) -> int:
    """Store a record in the database.

    Args:
        conn: An active psycopg connection.
        name: Name for the event record.
        data: Optional text data to store.
        table: Target table name.

    Returns:
        The id of the inserted record.
    """
    query = (
        f"INSERT INTO {table} (name, data, created_at) VALUES (%s, %s, %s) RETURNING id"
    )
    with conn.cursor() as cur:
        cur.execute(query, (name, data, datetime.now(timezone.utc)))
        result = cur.fetchone()
    conn.commit()
    record_id = result["id"]
    LOG.info("Stored record id=%d name='%s'", record_id, name)
    return record_id


def get_records(
    conn: psycopg.Connection,
    table: str = DEFAULT_TABLE,
    limit: int = 10,
) -> list[dict]:
    """Retrieve recent records from the database.

    Args:
        conn: An active psycopg connection.
        table: Source table name.
        limit: Maximum number of records to return.

    Returns:
        A list of record dictionaries.
    """
    query = f"SELECT id, name, data, created_at FROM {table} ORDER BY created_at DESC LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(query, (limit,))
        records = cur.fetchall()
    LOG.info("Retrieved %d records from '%s'", len(records), table)
    return records


KV_TABLE = "kv_store"


def create_kv_table(conn: psycopg.Connection) -> None:
    """Create the key-value store table if it does not exist.

    Args:
        conn: An active psycopg connection.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {KV_TABLE} (
        key VARCHAR(255) PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()
    LOG.info("Table '%s' is ready", KV_TABLE)


def kv_set(conn: psycopg.Connection, key: str, value: str) -> None:
    """Set a key-value pair, inserting or updating as needed.

    Args:
        conn: An active psycopg connection.
        key: The key to store.
        value: The value to associate with the key.
    """
    query = f"""
    INSERT INTO {KV_TABLE} (key, value, updated_at)
    VALUES (%s, %s, %s)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at
    """
    with conn.cursor() as cur:
        cur.execute(query, (key, value, datetime.now(timezone.utc)))
    conn.commit()
    LOG.info("Set key='%s'", key)


def kv_get(conn: psycopg.Connection, key: str) -> Optional[str]:
    """Get the value for a key.

    Args:
        conn: An active psycopg connection.
        key: The key to look up.

    Returns:
        The value if found, or None.
    """
    query = f"SELECT value FROM {KV_TABLE} WHERE key = %s"
    with conn.cursor() as cur:
        cur.execute(query, (key,))
        row = cur.fetchone()
    if row is None:
        LOG.debug("Key '%s' not found", key)
        return None
    return row["value"]


def kv_delete(conn: psycopg.Connection, key: str) -> bool:
    """Delete a key-value pair.

    Args:
        conn: An active psycopg connection.
        key: The key to delete.

    Returns:
        True if the key was deleted, False if it did not exist.
    """
    query = f"DELETE FROM {KV_TABLE} WHERE key = %s"
    with conn.cursor() as cur:
        cur.execute(query, (key,))
        deleted = cur.rowcount > 0
    conn.commit()
    if deleted:
        LOG.info("Deleted key='%s'", key)
    else:
        LOG.debug("Key '%s' not found for deletion", key)
    return deleted


def kv_list(conn: psycopg.Connection) -> list[dict]:
    """List all key-value pairs.

    Args:
        conn: An active psycopg connection.

    Returns:
        A list of dictionaries with key, value, and updated_at fields.
    """
    query = f"SELECT key, value, updated_at FROM {KV_TABLE} ORDER BY key"
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    LOG.info("Listed %d key-value pairs", len(rows))
    return rows
