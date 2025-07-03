"""Utility for running shell commands."""

from __future__ import annotations

import logging
import shlex
import subprocess
import sys
import threading
from typing import List

from halo import Halo


class Runner:
    """Helper to execute shell commands with a progress spinner."""

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize the runner."""
        self.dry_run = dry_run

    def run(self, args: List[str], text: str = "Running...") -> None:
        """Execute a shell command with a spinner."""
        cmd = " ".join(shlex.quote(arg) for arg in args)
        if self.dry_run:
            logging.info("DRY-RUN: %s", cmd)
            return

        spinner = Halo(text=text, spinner="dots")

        # Use a threading.Event to signal completion from the main thread
        finished = threading.Event()

        def spin() -> None:
            while not finished.is_set():
                spinner.tick()
                finished.wait(0.1)

        # Start the spinner in a separate thread
        spin_thread = threading.Thread(target=spin)
        spin_thread.start()

        try:
            logging.debug("Running command: %s", cmd)
            # Run the actual command, redirecting stdout/stderr
            result = subprocess.run(
                args,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            logging.debug("Command stdout:\n%s", result.stdout)
            if result.stderr:
                logging.debug("Command stderr:\n%s", result.stderr)
            spinner.succeed(f"{text} done.")
        except subprocess.CalledProcessError as e:
            spinner.fail(f"{text} failed.")
            logging.error("Command failed: %s", cmd)
            # Provide detailed error output for debugging
            logging.error("Return code: %d", e.returncode)
            logging.error("Stdout:\n%s", e.stdout)
            logging.error("Stderr:\n%s", e.stderr)
            sys.exit(1)  # Exit to prevent further operations
        finally:
            # Signal the spinner thread to stop and wait for it
            finished.set()
            spin_thread.join()
