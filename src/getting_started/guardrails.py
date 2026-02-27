"""
Regex-based guardrails scanner for detecting common code issues.

Scans files for hardcoded secrets, SQL injection risks, TODO comments,
hardcoded IPs/URLs, and debug statements left in production code.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import psycopg

LOG = logging.getLogger(__name__)

GUARDRAIL_TABLE = "guardrail_findings"


@dataclass
class ScanFinding:
    """A single finding from the guardrails scanner.

    Attributes:
        file_path: Absolute path to the file containing the finding.
        line_number: Line number where the finding was detected.
        pattern_name: Name of the regex pattern that matched.
        line_content: The full content of the matching line (stripped).
    """

    file_path: str
    line_number: int
    pattern_name: str
    line_content: str


@dataclass
class ScanResult:
    """Aggregated results from a guardrails scan.

    Attributes:
        scan_directory: The directory that was scanned.
        extensions: The file extensions that were included.
        findings: List of individual findings.
        scanned_at: Timestamp when the scan was performed.
    """

    scan_directory: str
    extensions: set[str]
    findings: list[ScanFinding] = field(default_factory=list)
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_findings(self) -> int:
        """Return the total number of findings."""
        return len(self.findings)

    def summary_by_pattern(self) -> dict[str, int]:
        """Return a count of findings grouped by pattern name.

        Returns:
            Dictionary mapping pattern names to their finding counts.
        """
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.pattern_name] = counts.get(finding.pattern_name, 0) + 1
        return counts


# Compiled regex patterns for common code issues
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "hardcoded_secret",
        re.compile(
            r"""(?i)(api[_-]?key|secret[_-]?key|password|passwd|token|auth[_-]?token)\s*[=:]\s*["'][^"']{4,}["']""",
        ),
    ),
    (
        "sql_injection_risk",
        re.compile(
            r"""(?i)(?:execute|cursor\.execute)\s*\(\s*(?:f["']|["'].*%s.*%|["'].*\+\s*\w+|["'].*\.format\()""",
        ),
    ),
    (
        "todo_fixme_hack",
        re.compile(
            r"""(?i)#\s*(?:TODO|FIXME|HACK|XXX|BUG)\b""",
        ),
    ),
    (
        "hardcoded_ip_or_url",
        re.compile(
            r"""(?:(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?|https?://[^\s"']+)""",
        ),
    ),
    (
        "debug_print_statement",
        re.compile(
            r"""(?:^|\s)(?:print\s*\(|breakpoint\s*\(|pdb\.set_trace\s*\()""",
        ),
    ),
]


def collect_files(directory: Path, extensions: set[str]) -> list[Path]:
    """Collect all files in a directory matching the given extensions.

    Args:
        directory: Root directory to scan.
        extensions: Set of file extensions to include (e.g., {".py", ".js"}).

    Returns:
        Sorted list of matching file paths.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Scan directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    files: list[Path] = []
    for ext in extensions:
        normalized_ext = ext if ext.startswith(".") else f".{ext}"
        files.extend(directory.rglob(f"*{normalized_ext}"))

    files.sort()
    LOG.debug(
        "Collected %d files from %s with extensions %s",
        len(files),
        directory,
        extensions,
    )
    return files


def scan_file(file_path: Path) -> list[ScanFinding]:
    """Scan a single file against all guardrail patterns.

    Args:
        file_path: Path to the file to scan.

    Returns:
        List of findings for the file.
    """
    findings: list[ScanFinding] = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        LOG.warning("Could not read file %s: %s", file_path, exc)
        return findings

    for line_number, line in enumerate(content.splitlines(), start=1):
        for pattern_name, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(
                    ScanFinding(
                        file_path=str(file_path.resolve()),
                        line_number=line_number,
                        pattern_name=pattern_name,
                        line_content=line.strip(),
                    )
                )

    return findings


def scan_directory(
    directory: Path,
    extensions: Optional[set[str]] = None,
) -> ScanResult:
    """Scan a directory for common code issues using regex patterns.

    Walks through all files matching the specified extensions and checks each
    line against a set of predefined regex patterns that detect hardcoded
    secrets, SQL injection risks, TODO comments, hardcoded IPs/URLs, and
    debug/print statements.

    Args:
        directory: Root directory to scan.
        extensions: File extensions to include. Defaults to {".py", ".js", ".yaml", ".yml"}.

    Returns:
        A ScanResult containing all findings.

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    if extensions is None:
        extensions = {".py", ".js", ".yaml", ".yml"}

    LOG.info("Starting guardrails scan of %s for extensions %s", directory, extensions)

    result = ScanResult(
        scan_directory=str(directory.resolve()),
        extensions=extensions,
    )

    files = collect_files(directory, extensions)
    for file_path in files:
        file_findings = scan_file(file_path)
        result.findings.extend(file_findings)

    LOG.info(
        "Guardrails scan complete: %d findings in %d files",
        result.total_findings,
        len(files),
    )
    return result


def create_guardrail_table(conn: psycopg.Connection) -> None:
    """Create the guardrail_findings table if it does not exist.

    Args:
        conn: An active psycopg connection.
    """
    query = f"""
    CREATE TABLE IF NOT EXISTS {GUARDRAIL_TABLE} (
        id SERIAL PRIMARY KEY,
        file_path TEXT NOT NULL,
        line_number INTEGER NOT NULL,
        pattern_name VARCHAR(255) NOT NULL,
        line_content TEXT,
        scanned_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()
    LOG.info("Table '%s' is ready", GUARDRAIL_TABLE)


def store_findings(conn: psycopg.Connection, result: ScanResult) -> int:
    """Store scan findings in the postgres database.

    Args:
        conn: An active psycopg connection.
        result: The scan result containing findings to store.

    Returns:
        The number of findings stored.
    """
    if not result.findings:
        LOG.info("No findings to store")
        return 0

    query = f"""
    INSERT INTO {GUARDRAIL_TABLE} (file_path, line_number, pattern_name, line_content, scanned_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        for finding in result.findings:
            cur.execute(
                query,
                (
                    finding.file_path,
                    finding.line_number,
                    finding.pattern_name,
                    finding.line_content,
                    result.scanned_at,
                ),
            )
    conn.commit()
    LOG.info(
        "Stored %d guardrail findings in '%s'", len(result.findings), GUARDRAIL_TABLE
    )
    return len(result.findings)
