"""Utility for running shell commands."""

from __future__ import annotations

import logging
import shlex
import subprocess
from typing import List, TypeVar

from rich.console import Console

from docker_ctp.utils.logging_utils import MessageHandler

T = TypeVar("T")


class Runner:
    """Helper to execute shell commands with a progress spinner."""

    def __init__(self, dry_run: bool = False, console: Console | None = None) -> None:
        """Initialize the runner.

        Args:
            dry_run: If True, commands will be logged but not executed.
            console: The Rich Console object to use for output.
        """
        self.dry_run = dry_run
        self.messages = MessageHandler(console=console)

    def _run_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Execute a shell command.

        Args:
            args: The command and its arguments as a list of strings.

        Returns:
            The completed process object.

        Raises:
            subprocess.CalledProcessError: If the command returns a non-zero exit code.
        """
        cmd = " ".join(shlex.quote(arg) for arg in args)
        logging.debug("Running command: %s", cmd)

        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def run(self, args: List[str], text: str = "Running...") -> None:
        """Execute a shell command with a spinner.

        Args:
            args: The command and its arguments as a list of strings.
            text: The text to display next to the spinner.

        Raises:
            subprocess.CalledProcessError: If the command returns a non-zero exit code.
        """
        if self.dry_run:
            self.messages.info(f"DRY-RUN: {' '.join(shlex.quote(arg) for arg in args)}")
            return

        def _execute() -> None:
            result = self._run_command(args)
            logging.debug("Command stdout:\n%s", result.stdout)
            if result.stderr:
                logging.debug("Command stderr:\n%s", result.stderr)

        self.messages.with_spinner(text, _execute)
