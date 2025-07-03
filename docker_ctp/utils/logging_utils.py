"""Logging utilities with ASCII art and progress."""

from __future__ import annotations

import logging
import sys
import time

ASCII_ART = """
d8888b.  .d88b.   .o88b. db   dD d88888b d8888b.                                 
88  `8D .8P  Y8. d8P  Y8 88 ,8P' 88'     88  `8D                                 
88   88 88    88 8P      88,8P   88ooooo 88oobY'                                 
88   88 88    88 8b      88`8b   88~~~~~ 88`8b                                   
88  .8D `8b  d8' Y8b  d8 88 `88. 88.     88 `88.                                 
Y8888D'  `Y88P'   `Y88P' YP   YD Y88888P 88   YD 
     
      Create, Tag and Push Docker images
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
