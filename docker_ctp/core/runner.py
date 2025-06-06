"""Utility for running shell commands."""

from __future__ import annotations

import logging
import shlex
import subprocess
from typing import List


class Runner:
    """Helper to execute shell commands."""

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize the runner."""
        self.dry_run = dry_run

    def run(self, args: List[str]) -> None:
        """Execute a shell command."""
        cmd = " ".join(shlex.quote(arg) for arg in args)
        if self.dry_run:
            logging.info("DRY-RUN %s", cmd)
            return
        logging.debug("Running command: %s", cmd)
        subprocess.run(args, check=True)
