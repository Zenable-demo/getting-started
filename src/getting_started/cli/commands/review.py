"""Review subcommand: interactively review findings."""

import argparse
import logging

from getting_started.storage import get_backend

LOG = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    """Interactively review findings and record decisions.

    Args:
        args: Parsed arguments with scan_id, storage_backend, loglevel.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    backend = get_backend(args.storage_backend)
    backend.connect()

    try:
        findings = backend.get_findings(limit=1000)
        if not findings:
            LOG.info("No findings to review")
            return 0

        LOG.info("Found %d findings to review", len(findings))
        reviewed = 0

        for finding in findings:
            print(f"\n{'=' * 60}")
            print(f"File: {finding.get('file_path')}")
            print(f"Line: {finding.get('line_number')}")
            print(f"Pattern: {finding.get('pattern_name')}")
            print(f"Content: {finding.get('line_content')}")
            print(f"{'=' * 60}")

            while True:
                decision = input("Decision (a=approve, r=reject, s=skip): ").lower()
                if decision in ("a", "r", "s"):
                    break
                print("Invalid choice. Enter 'a', 'r', or 's'.")

            if decision == "s":
                continue

            note = input("Optional note: ").strip() or None
            decision_str = "approve" if decision == "a" else "reject"
            backend.record_finding_decision(
                str(finding["id"]), decision_str, "interactive", note
            )
            reviewed += 1

        LOG.info("Reviewed %d findings", reviewed)
        return 0

    except Exception as e:
        LOG.error("Review failed: %s", e)
        return 1
    finally:
        backend.close()
