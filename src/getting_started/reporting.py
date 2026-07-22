"""
Reporting module: export scan results in various formats.

Supports JSON, CSV, SARIF, and Markdown output formats.
"""

import json
import logging

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
        "extensions": list(result.extensions),
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
    for pattern_name in result.summary_by_pattern().keys():
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
