"""Diff subcommand: compare two scans."""

import argparse
import logging

from getting_started.storage import get_backend

LOG = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    """Compare findings between two scans.

    Args:
        args: Parsed arguments with from_scan_id, to_scan_id, storage_backend.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    if not args.from_scan_id or not args.to_scan_id:
        LOG.error("Both --from-scan-id and --to-scan-id are required")
        return 1

    backend = get_backend(args.storage_backend)
    backend.connect()

    try:
        from_findings = backend.get_findings(limit=1000)
        to_findings = backend.get_findings(limit=1000)

        if not from_findings and not to_findings:
            LOG.info("No findings in either scan")
            return 0

        from_patterns = {}
        for f in from_findings:
            key = (f.get("file_path"), f.get("line_number"), f.get("pattern_name"))
            from_patterns[key] = f

        to_patterns = {}
        for f in to_findings:
            key = (f.get("file_path"), f.get("line_number"), f.get("pattern_name"))
            to_patterns[key] = f

        new_findings = set(to_patterns.keys()) - set(from_patterns.keys())
        removed_findings = set(from_patterns.keys()) - set(to_patterns.keys())
        unchanged = set(to_patterns.keys()) & set(from_patterns.keys())

        print("\nScan Comparison Report")
        print("=" * 60)
        print(f"New findings: {len(new_findings)}")
        print(f"Removed findings: {len(removed_findings)}")
        print(f"Unchanged findings: {len(unchanged)}")

        if new_findings:
            print(f"\n{'-' * 60}")
            print("New Findings:")
            for file_path, line_num, pattern in sorted(new_findings):
                print(f"  +{file_path}:{line_num} [{pattern}]")

        if removed_findings:
            print(f"\n{'-' * 60}")
            print("Removed Findings:")
            for file_path, line_num, pattern in sorted(removed_findings):
                print(f"  -{file_path}:{line_num} [{pattern}]")

        return 0

    except Exception as e:
        LOG.error("Diff failed: %s", e)
        return 1
    finally:
        backend.close()
