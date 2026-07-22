#!/usr/bin/env python3
"""
Test main.py module and CLI integration.
"""

import argparse
import logging
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
def test_parser_builds():
    """Test that the parser builds successfully"""
    from getting_started.cli.parser import build_parser

    parser = build_parser()
    assert parser is not None
    assert parser.prog == "getting-started"


@pytest.mark.unit
def test_scan_command_parsing():
    """Test that scan command is parsed correctly"""
    from getting_started.cli.parser import build_parser

    parser = build_parser()
    args = parser.parse_args(["scan", "test_dir"])
    assert args.command == "scan"
    assert args.path == "test_dir"


@pytest.mark.unit
def test_help_exit_code_zero():
    """Test that --help exits with code 0"""
    from getting_started.cli.parser import build_parser

    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])
    assert exc_info.value.code == 0


@pytest.mark.unit
def test_debug_verbose_mutually_exclusive():
    """Test that --debug and --verbose are mutually exclusive"""
    from getting_started.cli.parser import build_parser

    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--debug", "--verbose"])
    assert exc_info.value.code == 2


@pytest.mark.unit
def test_default_command_is_scan():
    """Test that default command is scan when no subcommand specified"""
    from getting_started.cli.dispatch import dispatch

    args = argparse.Namespace(
        command=None,
        path=".",
        format="json",
        output=None,
        interactive=False,
        max_findings=None,
        storage_backend="sqlite",
        loglevel=logging.WARNING,
    )

    mock_backend = MagicMock()
    mock_backend.connect = MagicMock()
    mock_backend.close = MagicMock()
    mock_backend.migrate = MagicMock()
    mock_backend.store_findings = MagicMock()

    with (
        patch("getting_started.config.setup_logging"),
        patch("getting_started.storage.get_backend", return_value=mock_backend),
        patch("getting_started.guardrails.scan_directory") as mock_scan,
    ):
        from getting_started.guardrails import ScanResult

        empty_result = ScanResult(scan_directory=".", extensions={".py"})
        mock_scan.return_value = empty_result

        exit_code = dispatch(args)
        assert exit_code == 0
        assert args.command == "scan"
