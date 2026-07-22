"""Entry point for `uv run python -m getting_started`."""

import sys

from getting_started.cli.dispatch import dispatch
from getting_started.cli.parser import build_parser

if __name__ == "__main__":
    args = build_parser().parse_args()
    sys.exit(dispatch(args))
