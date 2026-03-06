#!/usr/bin/env python3
"""
Test main.py module
"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from getting_started.guardrails import ScanResult


@pytest.mark.unit
def test_main_import():
    """Test that main.py can be imported without executing"""
    import main  # noqa: F401


@pytest.mark.unit
def test_main_function():
    """Test that main() connects to postgres, stores a record, and runs guardrails scan"""
    from main import main

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1}
    mock_cursor.fetchall.return_value = []
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    empty_scan_result = ScanResult(scan_directory=".", extensions={".py"})

    with (
        patch("getting_started.config.get_args_config") as mock_args,
        patch("main.connect", return_value=mock_conn),
        patch("main.create_table") as mock_create_table,
        patch("main.store_record", return_value=1) as mock_store_record,
        patch("main.get_records", return_value=[]) as mock_get_records,
        patch("main.create_kv_table") as mock_create_kv_table,
        patch("main.kv_set") as mock_kv_set,
        patch("main.kv_get", return_value="0.1.0") as mock_kv_get,
        patch("main.kv_list", return_value=[]) as mock_kv_list,
        patch("main.create_guardrail_table") as mock_create_guardrail_table,
        patch(
            "main.scan_directory", return_value=empty_scan_result
        ) as mock_scan_directory,
        patch("main.store_findings", return_value=0) as mock_store_findings,
        patch("getting_started.config.get_scan_dir", return_value="."),
    ):
        mock_args.return_value = {"loglevel": logging.WARNING, "scan_dir": "."}
        main()

        mock_create_table.assert_called_once_with(mock_conn)
        mock_store_record.assert_called_once_with(
            mock_conn, name="startup", data="Application started successfully"
        )
        mock_get_records.assert_called_once_with(mock_conn)
        mock_create_kv_table.assert_called_once_with(mock_conn)
        assert mock_kv_set.call_count == 2
        mock_kv_get.assert_called_once_with(mock_conn, "app.version")
        mock_kv_list.assert_called_once_with(mock_conn)
        mock_create_guardrail_table.assert_called_once_with(mock_conn)
        mock_scan_directory.assert_called_once()
        mock_store_findings.assert_called_once_with(mock_conn, empty_scan_result)
        mock_conn.close.assert_called_once()
