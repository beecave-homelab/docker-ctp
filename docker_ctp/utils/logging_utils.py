"""Logging utilities with ASCII art and progress."""

from __future__ import annotations

import logging
import sys
import time

ASCII_ART = r"""
██████   ██████   ██████ ██   ██ ███████ ██████
██   ██ ██    ██ ██      ██  ██  ██      ██   ██
██   ██ ██    ██ ██      █████   █████   ██████
██   ██ ██    ██ ██      ██  ██  ██      ██   ██
██████   ██████   ██████ ██   ██ ███████ ██   ██
"""


def print_ascii_art(dry_run: bool) -> None:
    """Print ASCII art banner."""
    if logging.getLogger().level <= logging.INFO:
        logging.info("\n%s", ASCII_ART)
        if dry_run:
            logging.info("DRY RUN MODE - No commands executed")


def progress(message: str, duration: int = 3) -> None:
    """Display a simple textual progress indicator."""
    if logging.getLogger().level > logging.INFO:
        return
    sys.stdout.write(message)
    sys.stdout.flush()
    for _ in range(duration):
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write(" Done!\n")
    sys.stdout.flush()
