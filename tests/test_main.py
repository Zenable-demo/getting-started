#!/usr/bin/env python3
"""
Test main.py module
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
def test_main_import():
    """Test that main.py can be imported without executing"""
    import main  # noqa: F401


@pytest.mark.unit
def test_main_function():
    """Test that main() connects to postgres and stores a record"""
    from main import main

    import logging

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1}
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with (
        patch("getting_started.config.get_args_config") as mock_args,
        patch("main.connect", return_value=mock_conn),
        patch("main.create_table") as mock_create_table,
        patch("main.store_record", return_value=1) as mock_store_record,
        patch("main.get_records", return_value=[]) as mock_get_records,
    ):
        mock_args.return_value = {"loglevel": logging.WARNING}
        main()

        mock_create_table.assert_called_once_with(mock_conn)
        mock_store_record.assert_called_once_with(mock_conn, name="startup", data="Application started successfully")
        mock_get_records.assert_called_once_with(mock_conn)
        mock_conn.close.assert_called_once()
