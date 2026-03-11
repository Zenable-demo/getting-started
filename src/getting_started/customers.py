"""
Customer data management for getting-started.

Provides CRUD operations for storing and retrieving customer records
in PostgreSQL.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import psycopg

LOG = logging.getLogger(__name__)

CUSTOMER_TABLE = "customers"


def create_customer_table(conn: psycopg.Connection) -> None:
    """Create the customers table if it does not exist.

    Args:
        conn: An active psycopg connection.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {CUSTOMER_TABLE} (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        company VARCHAR(255),
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()
    LOG.info("Table '%s' is ready", CUSTOMER_TABLE)


def create_customer(
    conn: psycopg.Connection,
    name: str,
    email: str,
    company: Optional[str] = None,
) -> int:
    """Create a new customer record.

    Args:
        conn: An active psycopg connection.
        name: Customer's full name.
        email: Customer's email address (must be unique).
        company: Optional company name.

    Returns:
        The id of the newly created customer.

    Raises:
        psycopg.errors.UniqueViolation: If a customer with the same email exists.
    """
    now = datetime.now(timezone.utc)
    query = f"""
    INSERT INTO {CUSTOMER_TABLE} (name, email, company, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    with conn.cursor() as cur:
        cur.execute(query, (name, email, company, now, now))
        result = cur.fetchone()
    conn.commit()
    customer_id = result["id"]
    LOG.info("Created customer id=%d name='%s' email='%s'", customer_id, name, email)
    return customer_id


def get_customer(conn: psycopg.Connection, customer_id: int) -> Optional[dict]:
    """Get a customer by id.

    Args:
        conn: An active psycopg connection.
        customer_id: The customer's id.

    Returns:
        A customer dictionary, or None if not found.
    """
    query = f"SELECT id, name, email, company, status, created_at, updated_at FROM {CUSTOMER_TABLE} WHERE id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (customer_id,))
        row = cur.fetchone()
    if row is None:
        LOG.debug("Customer id=%d not found", customer_id)
        return None
    return row


def get_customer_by_email(conn: psycopg.Connection, email: str) -> Optional[dict]:
    """Get a customer by email address.

    Args:
        conn: An active psycopg connection.
        email: The customer's email address.

    Returns:
        A customer dictionary, or None if not found.
    """
    query = f"SELECT id, name, email, company, status, created_at, updated_at FROM {CUSTOMER_TABLE} WHERE email = %s"
    with conn.cursor() as cur:
        cur.execute(query, (email,))
        row = cur.fetchone()
    if row is None:
        LOG.debug("Customer with email='%s' not found", email)
        return None
    return row


def list_customers(
    conn: psycopg.Connection,
    limit: int = 10,
) -> list[dict]:
    """List customers ordered by creation date.

    Args:
        conn: An active psycopg connection.
        limit: Maximum number of customers to return.

    Returns:
        A list of customer dictionaries.
    """
    query = f"SELECT id, name, email, company, status, created_at, updated_at FROM {CUSTOMER_TABLE} ORDER BY created_at DESC LIMIT %s"
    with conn.cursor() as cur:
        cur.execute(query, (limit,))
        rows = cur.fetchall()
    LOG.info("Listed %d customers", len(rows))
    return rows


def update_customer(
    conn: psycopg.Connection,
    customer_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None,
    status: Optional[str] = None,
) -> bool:
    """Update a customer's fields.

    Only the provided (non-None) fields are updated. The updated_at
    timestamp is always refreshed.

    Args:
        conn: An active psycopg connection.
        customer_id: The customer's id.
        name: New name, if updating.
        email: New email, if updating.
        company: New company, if updating.
        status: New status, if updating.

    Returns:
        True if the customer was updated, False if not found.

    Raises:
        ValueError: If no fields are provided to update.
        psycopg.errors.UniqueViolation: If the new email conflicts with an existing customer.
    """
    allowed_fields = {
        "name": name,
        "email": email,
        "company": company,
        "status": status,
    }
    updates = {k: v for k, v in allowed_fields.items() if v is not None}
    if not updates:
        raise ValueError("At least one field must be provided for update")

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values = list(updates.values()) + [datetime.now(timezone.utc), customer_id]
    query = f"UPDATE {CUSTOMER_TABLE} SET {set_clause}, updated_at = %s WHERE id = %s"

    with conn.cursor() as cur:
        cur.execute(query, values)
        updated = cur.rowcount > 0
    conn.commit()
    if updated:
        LOG.info("Updated customer id=%d fields=%s", customer_id, list(updates.keys()))
    else:
        LOG.debug("Customer id=%d not found for update", customer_id)
    return updated


def delete_customer(conn: psycopg.Connection, customer_id: int) -> bool:
    """Delete a customer by id.

    Args:
        conn: An active psycopg connection.
        customer_id: The customer's id.

    Returns:
        True if the customer was deleted, False if not found.
    """
    query = f"DELETE FROM {CUSTOMER_TABLE} WHERE id = %s"
    with conn.cursor() as cur:
        cur.execute(query, (customer_id,))
        deleted = cur.rowcount > 0
    conn.commit()
    if deleted:
        LOG.info("Deleted customer id=%d", customer_id)
    else:
        LOG.debug("Customer id=%d not found for deletion", customer_id)
    return deleted
