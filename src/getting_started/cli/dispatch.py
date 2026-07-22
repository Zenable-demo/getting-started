"""
Central CLI dispatcher: routes parsed args to the appropriate command handler.

Exception → exit-code mapping:
- OperationalError (connection error) → 1 (from uncaught psycopg exception)
- argparse errors → 2 (mutually exclusive flags, etc.)
- All others → 1 (unless a command handler catches and returns a different code)
"""

import argparse
import logging

from getting_started import config

LOG = logging.getLogger(__name__)


def dispatch(args: argparse.Namespace) -> int:
    """Dispatch parsed arguments to the appropriate command handler.

    Args:
        args: Parsed command-line arguments from the parser.

    Returns:
        Exit code (0 = success, 1 = error, 2 = usage error).

    Raises:
        psycopg.OperationalError: Connection errors propagate uncaught
                                  (intentional: matches integration test expectations).
    """
    config.setup_logging(loglevel=args.loglevel)

    # Default to "scan" if no subcommand specified
    args.command = args.command or "scan"

    LOG.debug("Dispatching command: %s", args.command)

    if args.command == "scan":
        from getting_started.cli.commands import scan

        return scan.run(args)
    elif args.command == "watch":
        from getting_started.cli.commands import watch

        return watch.run(args)
    elif args.command == "diff":
        from getting_started.cli.commands import diff

        return diff.run(args)
    elif args.command == "review":
        from getting_started.cli.commands import review

        return review.run(args)
    elif args.command == "hook":
        from getting_started.cli.commands import hook

        return hook.run(args)
    elif args.command == "serve":
        from getting_started.cli.commands import serve

        return serve.run(args)
    else:
        LOG.error("Unknown command: %s", args.command)
        return 1
