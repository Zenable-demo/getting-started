"""
PostgreSQL database integration for getting-started.

All sensitive data is encrypted at rest using per-customer keys.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import psycopg
from psycopg.rows import dict_row

from getting_started.encryption import decrypt, encrypt

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
        customer_id VARCHAR(255) NOT NULL,
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
    customer_id: str,
    data: Optional[str] = None,
    table: str = DEFAULT_TABLE,
) -> int:
    """Store a record in the database with per-customer encryption.

    The data field is encrypted using a key derived from the customer_id
    before being written to the database.

    Args:
        conn: An active psycopg connection.
        name: Name for the event record.
        customer_id: Customer identifier used for encryption key derivation.
        data: Optional text data to store (will be encrypted).
        table: Target table name.

    Returns:
        The id of the inserted record.
    """
    encrypted_data = encrypt(data, customer_id)
    query = (
        f"INSERT INTO {table} (customer_id, name, data, created_at) "
        f"VALUES (%s, %s, %s, %s) RETURNING id"
    )
    with conn.cursor() as cur:
        cur.execute(query, (customer_id, name, encrypted_data, datetime.now(timezone.utc)))
        result = cur.fetchone()
    conn.commit()
    record_id = result["id"]
    LOG.info("Stored record id=%d name='%s' customer_id='%s'", record_id, name, customer_id)
    return record_id


def get_records(
    conn: psycopg.Connection,
    customer_id: str,
    table: str = DEFAULT_TABLE,
    limit: int = 10,
) -> list[dict]:
    """Retrieve recent records for a customer, decrypting data fields.

    Only returns records belonging to the specified customer. The data
    field is decrypted using the customer's derived key.

    Args:
        conn: An active psycopg connection.
        customer_id: Customer identifier used for decryption and filtering.
        table: Source table name.
        limit: Maximum number of records to return.

    Returns:
        A list of record dictionaries with decrypted data.
    """
    query = (
        f"SELECT id, customer_id, name, data, created_at FROM {table} "
        f"WHERE customer_id = %s ORDER BY created_at DESC LIMIT %s"
    )
    with conn.cursor() as cur:
        cur.execute(query, (customer_id, limit))
        records = cur.fetchall()

    for record in records:
        record["data"] = decrypt(record["data"], customer_id)

    LOG.info("Retrieved %d records from '%s' for customer '%s'", len(records), table, customer_id)
    return records
