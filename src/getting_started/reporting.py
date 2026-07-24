"""
Reporting module: export scan results in various formats.

Supports JSON, CSV, SARIF, and Markdown output formats.
"""

import json
import logging
from collections.abc import Callable
from pathlib import Path

from getting_started.guardrails import ScanResult

LOG = logging.getLogger(__name__)


def to_json(result: ScanResult) -> str:
    """Export scan result as JSON.

    Args:
        result: The scan result.

    Returns:
        JSON string.
    """
    data = {
        "scan_directory": result.scan_directory,
        "extensions": sorted(result.extensions),
        "scanned_at": result.scanned_at.isoformat(),
        "total_findings": result.total_findings,
        "findings": [
            {
                "file_path": f.file_path,
                "line_number": f.line_number,
                "pattern_name": f.pattern_name,
                "line_content": f.line_content,
            }
            for f in result.findings
        ],
        "summary": result.summary_by_pattern(),
    }
    return json.dumps(data, indent=2)


def to_csv(result: ScanResult) -> str:
    """Export scan result as CSV.

    Args:
        result: The scan result.

    Returns:
        CSV string.
    """
    lines = ["file_path,line_number,pattern_name,line_content"]
    for finding in result.findings:
        content = finding.line_content.replace('"', '""')
        lines.append(
            f'"{finding.file_path}",{finding.line_number},"{finding.pattern_name}","{content}"'
        )
    return "\n".join(lines)


def to_sarif(result: ScanResult) -> str:
    """Export scan result as SARIF (Static Analysis Results Interchange Format).

    Args:
        result: The scan result.

    Returns:
        SARIF JSON string.
    """
    rules = {}
    for pattern_name in result.summary_by_pattern():
        rules[pattern_name] = {
            "id": pattern_name,
            "shortDescription": {"text": f"Guardrail: {pattern_name}"},
            "helpUri": "https://github.com/zenable-demo/getting-started#guardrails",
        }

    results = []
    for finding in result.findings:
        results.append(
            {
                "ruleId": finding.pattern_name,
                "message": {"text": finding.line_content},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": finding.file_path},
                            "region": {"startLine": finding.line_number},
                        }
                    }
                ],
            }
        )

    sarif_obj = {
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "getting-started-guardrails",
                        "version": "0.1.0",
                        "rules": [v for v in rules.values()],
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif_obj, indent=2)


def to_markdown(result: ScanResult) -> str:
    """Export scan result as Markdown.

    Args:
        result: The scan result.

    Returns:
        Markdown string.
    """
    lines = [
        "# Guardrails Scan Report",
        "",
        f"**Directory:** `{result.scan_directory}`",
        f"**Scanned At:** {result.scanned_at.isoformat()}",
        f"**Total Findings:** {result.total_findings}",
        "",
    ]

    summary = result.summary_by_pattern()
    if summary:
        lines.extend(
            [
                "## Summary by Pattern",
                "",
            ]
        )
        for pattern, count in sorted(summary.items()):
            lines.append(f"- **{pattern}:** {count}")
        lines.append("")

    if result.findings:
        lines.extend(
            [
                "## Findings",
                "",
            ]
        )
        for i, finding in enumerate(result.findings, 1):
            lines.extend(
                [
                    f"### {i}. {finding.pattern_name}",
                    f"**File:** `{finding.file_path}:{finding.line_number}`",
                    f"**Content:** `{finding.line_content}`",
                    "",
                ]
            )

    return "\n".join(lines)


def render_report(result: ScanResult, output_format: str) -> str:
    """Render a scan result in the requested output format.

    Args:
        result: The scan result.
        output_format: One of json, csv, sarif, or markdown.

    Returns:
        The rendered report.

    Raises:
        ValueError: If the output format is unsupported.
    """
    renderers: dict[str, Callable[[ScanResult], str]] = {
        "json": to_json,
        "csv": to_csv,
        "sarif": to_sarif,
        "markdown": to_markdown,
    }

    try:
        renderer = renderers[output_format]
    except KeyError as exc:
        supported_formats = ", ".join(renderers)
        raise ValueError(
            f"Unsupported report format '{output_format}'. "
            f"Choose from: {supported_formats}"
        ) from exc

    return renderer(result)


def write_report(
    result: ScanResult,
    output_format: str,
    output_path: Path | None = None,
) -> None:
    """Write a rendered scan report to a file or standard output.

    Args:
        result: The scan result.
        output_format: One of json, csv, sarif, or markdown.
        output_path: Destination file. When omitted, write to standard output.
    """
    report = render_report(result, output_format)

    if output_path is None:
        print(report)
        return

    output_path.write_text(f"{report}\n", encoding="utf-8")
    LOG.info("Wrote %s report to %s", output_format, output_path)
