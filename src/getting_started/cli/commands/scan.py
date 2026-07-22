"""
Scan subcommand: the core guardrails scanning logic, ported from the original main().

This is the default command when no subcommand is specified, preserving
the original behavior of `docker run image` (no args).
"""

import argparse
import logging
from pathlib import Path

from getting_started.guardrails import scan_directory
from getting_started.storage import get_backend

LOG = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    """Run a guardrails scan and store findings.

    Args:
        args: Parsed command-line arguments with:
          - path: Directory to scan
          - format: Output format (json, csv, sarif, markdown)
          - output: Output file (None = stdout)
          - interactive: Whether to enter interactive review after scan
          - max_findings: Maximum findings to return
          - storage_backend: Backend to use (postgres or sqlite)
          - loglevel: Logging level

    Returns:
        0 if successful, 1 on error.

    Raises:
        psycopg.OperationalError: If backend connection fails (intentional,
                                  preserved for integration test compatibility).
    """
    backend = get_backend(args.storage_backend)
    backend.connect()

    try:
        backend.migrate()

        scan_dir = Path(args.path or ".")
        LOG.info("Starting guardrails scan of %s", scan_dir)

        result = scan_directory(scan_dir)
        LOG.info(
            "Scan complete: %d findings in %d files",
            result.total_findings,
            len([f for f in scan_dir.rglob("*") if f.is_file()]),
        )

        backend.store_findings(result)

        summary = result.summary_by_pattern()
        for pattern_name, count in summary.items():
            LOG.info("  %s: %d finding(s)", pattern_name, count)

        if getattr(args, "interactive", False):
            LOG.info("Entering interactive review mode...")

        output = getattr(args, "output", None)
        if output:
            output_format = getattr(args, "format", "json")
            LOG.info("Would export to %s in %s format", output, output_format)

        return 0

    except Exception as e:
        LOG.error("Scan failed: %s", e)
        return 1
    finally:
        backend.close()
