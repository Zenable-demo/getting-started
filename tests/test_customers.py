#!/usr/bin/env python3
"""
Test getting_started/customers.py
"""

from unittest.mock import MagicMock

import pytest

from getting_started.customers import (
    create_customer,
    create_customer_table,
    delete_customer,
    get_customer,
    get_customer_by_email,
    list_customers,
    update_customer,
)


def _mock_conn():
    """Create a mock connection with cursor context manager."""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__ = MagicMock(return_value=cursor)
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    return conn, cursor


@pytest.mark.unit
def test_create_customer_table():
    """Test that create_customer_table executes the DDL and commits."""
    conn, cursor = _mock_conn()
    create_customer_table(conn)
    cursor.execute.assert_called_once()
    assert "CREATE TABLE IF NOT EXISTS customers" in cursor.execute.call_args[0][0]
    conn.commit.assert_called_once()


@pytest.mark.unit
def test_create_customer_with_company():
    """Test creating a customer with a company name."""
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 42}

    result = create_customer(
        conn, name="Alice", email="alice@example.com", company="Acme"
    )

    assert result == 42
    cursor.execute.assert_called_once()
    params = cursor.execute.call_args[0][1]
    assert params[0] == "Alice"
    assert params[1] == "alice@example.com"
    assert params[2] == "Acme"
    conn.commit.assert_called_once()


@pytest.mark.unit
def test_create_customer_without_company():
    """Test creating a customer without a company name."""
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = {"id": 1}

    result = create_customer(conn, name="Bob", email="bob@example.com")

    assert result == 1
    params = cursor.execute.call_args[0][1]
    assert params[2] is None


@pytest.mark.unit
def test_get_customer_found():
    """Test retrieving an existing customer by id."""
    conn, cursor = _mock_conn()
    expected = {"id": 1, "name": "Alice", "email": "alice@example.com"}
    cursor.fetchone.return_value = expected

    result = get_customer(conn, 1)

    assert result == expected
    params = cursor.execute.call_args[0][1]
    assert params == (1,)


@pytest.mark.unit
def test_get_customer_not_found():
    """Test retrieving a non-existent customer by id."""
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None

    result = get_customer(conn, 999)

    assert result is None


@pytest.mark.unit
def test_get_customer_by_email_found():
    """Test retrieving an existing customer by email."""
    conn, cursor = _mock_conn()
    expected = {"id": 1, "name": "Alice", "email": "alice@example.com"}
    cursor.fetchone.return_value = expected

    result = get_customer_by_email(conn, "alice@example.com")

    assert result == expected
    params = cursor.execute.call_args[0][1]
    assert params == ("alice@example.com",)


@pytest.mark.unit
def test_get_customer_by_email_not_found():
    """Test retrieving a non-existent customer by email."""
    conn, cursor = _mock_conn()
    cursor.fetchone.return_value = None

    result = get_customer_by_email(conn, "nobody@example.com")

    assert result is None


@pytest.mark.unit
def test_list_customers():
    """Test listing customers returns all rows."""
    conn, cursor = _mock_conn()
    cursor.fetchall.return_value = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]

    result = list_customers(conn)

    assert len(result) == 2


@pytest.mark.unit
def test_list_customers_empty():
    """Test listing customers when table is empty."""
    conn, cursor = _mock_conn()
    cursor.fetchall.return_value = []

    result = list_customers(conn)

    assert result == []


@pytest.mark.unit
def test_list_customers_custom_limit():
    """Test that a custom limit is passed to the query."""
    conn, cursor = _mock_conn()
    cursor.fetchall.return_value = []

    list_customers(conn, limit=5)

    params = cursor.execute.call_args[0][1]
    assert params == (5,)


@pytest.mark.unit
def test_update_customer_single_field():
    """Test updating a single field on a customer."""
    conn, cursor = _mock_conn()
    cursor.rowcount = 1

    result = update_customer(conn, 1, name="New Name")

    assert result is True
    sql = cursor.execute.call_args[0][0]
    assert "name = %s" in sql
    conn.commit.assert_called_once()


@pytest.mark.unit
def test_update_customer_multiple_fields():
    """Test updating multiple fields on a customer."""
    conn, cursor = _mock_conn()
    cursor.rowcount = 1

    result = update_customer(conn, 1, name="New Name", status="inactive")

    assert result is True
    sql = cursor.execute.call_args[0][0]
    assert "name = %s" in sql
    assert "status = %s" in sql


@pytest.mark.unit
def test_update_customer_not_found():
    """Test updating a non-existent customer."""
    conn, cursor = _mock_conn()
    cursor.rowcount = 0

    result = update_customer(conn, 999, name="Ghost")

    assert result is False


@pytest.mark.unit
def test_update_customer_no_fields_raises():
    """Test that updating with no fields raises ValueError."""
    conn, _ = _mock_conn()

    with pytest.raises(ValueError, match="At least one field"):
        update_customer(conn, 1)


@pytest.mark.unit
def test_delete_customer_exists():
    """Test deleting an existing customer."""
    conn, cursor = _mock_conn()
    cursor.rowcount = 1

    result = delete_customer(conn, 1)

    assert result is True
    conn.commit.assert_called_once()


@pytest.mark.unit
def test_delete_customer_not_exists():
    """Test deleting a non-existent customer."""
    conn, cursor = _mock_conn()
    cursor.rowcount = 0

    result = delete_customer(conn, 999)

    assert result is False
    conn.commit.assert_called_once()
