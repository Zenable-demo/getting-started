"""Watch subcommand: auto-rescan on file changes."""

import argparse
import logging
from pathlib import Path

import watchfiles

from getting_started.cli.commands.scan import run as run_scan

LOG = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    """Watch directory for file changes and rescan on each change.

    Args:
        args: Parsed arguments with path, watch_debounce, storage_backend.

    Returns:
        Exit code (0 = success).
    """
    path = Path(args.path or ".")
    if not path.exists():
        LOG.error("Path does not exist: %s", path)
        return 1

    LOG.info("Watching %s for changes (debounce: %sms)", path, args.watch_debounce)

    try:
        for changes in watchfiles.watch(
            str(path),
            watch_filter=watchfiles.DefaultFilter(),
            debounce=args.watch_debounce,
        ):
            if changes:
                LOG.info("Detected %d file changes, running scan...", len(changes))
                exit_code = run_scan(args)
                if exit_code != 0:
                    LOG.warning("Scan exited with code %d", exit_code)

    except KeyboardInterrupt:
        LOG.info("Watch mode stopped by user")
        return 0
    except Exception as e:
        LOG.error("Watch failed: %s", e)
        return 1
