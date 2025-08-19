"""AIWB Cli entry point."""

import logging
import os
import sys

from aiwb.cli import cli_group
from aiwb.utils.console import console

from rich.logging import RichHandler


def _extract_verbose_flags(argv: list[str]) -> tuple[int, list[str]]:
    """Count and strip -v/--verbose flags anywhere in argv.

    """
    count = 0
    rest: list[str] = []
    for tok in argv:
        if tok in ("-v", "--verbose"):
            count += 1
            continue
        rest.append(tok)
        if tok == "--debug":
            count += 2
            continue
    return count, rest


def main():
    # Pre-parse verbosity flags so users can put them anywhere (before/after subcommands)
    vcount, remaining = _extract_verbose_flags(sys.argv[1:])
    sys.argv = [sys.argv[0], *remaining]
    # if vcount == 2 then debug, if vcount == 1 then verbose, else default to warning
    level = logging.WARNING
    if vcount >= 2 or os.getenv("AIWB_DEBUG") in ("1", "True"):
        level = logging.DEBUG
    elif vcount == 1 or os.getenv("AIWB_VERBOSE") in ("1", "True"):
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_path=False)],
    )
    cli_group()
