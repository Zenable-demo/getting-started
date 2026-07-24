"""Tests for scan report rendering and output."""

import json
from argparse import Namespace
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from getting_started.cli.commands.scan import run
from getting_started.guardrails import ScanFinding, ScanResult
from getting_started.reporting import render_report


@pytest.fixture
def scan_result() -> ScanResult:
    """Create a stable scan result for report assertions."""
    return ScanResult(
        scan_directory="/workspace",
        extensions={".py"},
        findings=[
            ScanFinding(
                file_path="/workspace/example.py",
                line_number=3,
                pattern_name="debug_print_statement",
                line_content='print("debug")',
            )
        ],
        scanned_at=datetime(2026, 7, 24, 12, 0, tzinfo=UTC),
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("output_format", "expected_text"),
    [
        ("json", '"total_findings": 1'),
        ("csv", "file_path,line_number,pattern_name,line_content"),
        ("sarif", '"version": "2.1.0"'),
        ("markdown", "# Guardrails Scan Report"),
    ],
)
def test_render_report_supports_cli_formats(
    scan_result: ScanResult,
    output_format: str,
    expected_text: str,
) -> None:
    """Render every report format accepted by the CLI."""
    assert expected_text in render_report(scan_result, output_format)


@pytest.mark.unit
def test_scan_writes_report_to_file(
    tmp_path,
    scan_result: ScanResult,
) -> None:
    """Write the selected report format to the requested file."""
    output_path = tmp_path / "scan.md"
    args = Namespace(
        path="/workspace",
        format="markdown",
        output=str(output_path),
        interactive=False,
        storage_backend="sqlite",
    )
    backend = MagicMock()

    with (
        patch(
            "getting_started.cli.commands.scan.get_backend",
            return_value=backend,
        ),
        patch(
            "getting_started.cli.commands.scan.scan_directory",
            return_value=scan_result,
        ),
    ):
        exit_code = run(args)

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8").startswith(
        "# Guardrails Scan Report\n"
    )
    backend.store_findings.assert_called_once_with(scan_result)
    backend.close.assert_called_once()


@pytest.mark.unit
def test_scan_writes_json_report_to_stdout(
    capsys,
    scan_result: ScanResult,
) -> None:
    """Write JSON to standard output when no output file is provided."""
    args = Namespace(
        path="/workspace",
        format="json",
        output=None,
        interactive=False,
        storage_backend="sqlite",
    )
    backend = MagicMock()

    with (
        patch(
            "getting_started.cli.commands.scan.get_backend",
            return_value=backend,
        ),
        patch(
            "getting_started.cli.commands.scan.scan_directory",
            return_value=scan_result,
        ),
    ):
        exit_code = run(args)

    report = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert report["total_findings"] == 1
    assert report["findings"][0]["pattern_name"] == "debug_print_statement"
