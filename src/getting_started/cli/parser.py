"""
Argument parser for the CLI.

Maintains the existing top-level `--version` and mutually-exclusive
`--debug`/`--verbose` flags, and adds subcommands for scan, serve, watch, etc.
"""

import argparse
import logging

from getting_started import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Preserves existing behavior:
    - `docker run image` (no args) → scan (default command)
    - `docker run image --debug --verbose` → exit 2 (mutually exclusive error)
    - `docker run image --help` → exit 0 with help text

    Returns:
        A configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="getting-started",
        description="A playground for getting started with Zenable",
    )

    parser.add_argument("--version", action="version", version=__version__)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--debug",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        help="enable debug logging",
    )
    group.add_argument(
        "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
        help="enable informational logging",
    )
    parser.set_defaults(loglevel=logging.WARNING)

    parser.add_argument(
        "--storage-backend",
        type=str,
        default=None,
        help="storage backend: postgres or sqlite (default: postgres)",
    )

    subparsers = parser.add_subparsers(dest="command", help="subcommand")

    # scan subcommand (default)
    scan_parser = subparsers.add_parser("scan", help="scan a directory for issues")
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to scan (default: current directory)",
    )
    scan_parser.add_argument(
        "--format",
        choices=["json", "csv", "sarif", "markdown"],
        default="json",
        help="output format (default: json)",
    )
    scan_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="output file (default: stdout)",
    )
    scan_parser.add_argument(
        "--interactive",
        action="store_true",
        help="interactive review mode after scan",
    )
    scan_parser.add_argument(
        "--max-findings",
        type=int,
        default=None,
        help="maximum findings to return",
    )

    # watch subcommand
    watch_parser = subparsers.add_parser(
        "watch", help="watch for file changes and scan"
    )
    watch_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to watch and scan (default: current directory)",
    )
    watch_parser.add_argument(
        "--watch-debounce",
        type=int,
        default=500,
        help="debounce interval in ms (default: 500)",
    )

    # diff subcommand
    diff_parser = subparsers.add_parser("diff", help="compare two scans")
    diff_parser.add_argument(
        "--from-scan-id",
        type=str,
        help="ID of first scan to compare",
    )
    diff_parser.add_argument(
        "--to-scan-id",
        type=str,
        help="ID of second scan to compare",
    )

    # review subcommand
    review_parser = subparsers.add_parser(
        "review", help="interactively review findings"
    )
    review_parser.add_argument(
        "--scan-id",
        type=str,
        default=None,
        help="scan ID to review (default: latest)",
    )

    # hook subcommand
    hook_parser = subparsers.add_parser("hook", help="git pre-commit hook")
    hook_parser.add_argument(
        "--max-findings",
        type=int,
        default=0,
        help="fail if findings >= this threshold (default: 0)",
    )
    hook_parser.add_argument(
        "--hook-install",
        action="store_true",
        help="install as .git/hooks/pre-commit",
    )
    hook_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="directory to scan (default: current directory)",
    )

    # serve subcommand
    serve_parser = subparsers.add_parser("serve", help="run the API server")
    serve_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="API host (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port (default: 8000)",
    )

    return parser
