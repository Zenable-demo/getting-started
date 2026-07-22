#!/usr/bin/env python3
"""
getting-started CLI entrypoint.

Parses arguments and dispatches to the appropriate command handler.
"""

import sys

from getting_started.cli.dispatch import dispatch
from getting_started.cli.parser import build_parser


def main() -> int:
    """Parse arguments and dispatch to the appropriate command.

    Returns:
        Exit code for the process.
    """
    args = build_parser().parse_args()
    return dispatch(args)


if __name__ == "__main__":
    sys.exit(main())
