"""Hook subcommand: git pre-commit hook integration."""

import argparse
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    """Run as a git pre-commit hook or install the hook.

    Args:
        args: Parsed arguments with max_findings, install, hook_install.

    Returns:
        Exit code (0 = pass, 1 = findings >= threshold, 2 = error).
    """
    if args.hook_install:
        return _install_hook()

    git_root = Path.cwd()
    hooks_dir = git_root / ".git" / "hooks"
    if not hooks_dir.exists():
        LOG.error("Not a git repository")
        return 2

    from getting_started.cli.commands.scan import run as run_scan

    LOG.info("Running pre-commit hook scan (max findings: %d)", args.max_findings)
    exit_code = run_scan(args)
    if exit_code != 0:
        return exit_code

    LOG.info("Hook scan passed")
    return 0


def _install_hook() -> int:
    """Install the pre-commit hook."""
    git_root = Path.cwd()
    hooks_dir = git_root / ".git" / "hooks"

    if not hooks_dir.exists():
        LOG.error("Not a git repository")
        return 2

    hook_path = hooks_dir / "pre-commit"
    hook_script = """#!/bin/bash
set -e
uv run --frozen python src/main.py hook "$@"
"""

    hook_path.write_text(hook_script)
    hook_path.chmod(0o755)
    LOG.info("Installed pre-commit hook at %s", hook_path)
    return 0
