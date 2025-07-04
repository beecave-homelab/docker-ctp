"""Dependency checking utilities."""

from __future__ import annotations

import shutil
import subprocess
from typing import Optional

from docker_ctp.core.runner import Runner
from docker_ctp.exceptions import DependencyError

__all__: list[str] = [
    "check_dependencies",
]


def check_dependencies(runner: Optional[Runner] = None, dry_run: bool = False) -> None:  # noqa: D401
    """Verify that Docker is installed and the daemon is running.

    Args:
        runner: Optional Runner instance to use for command execution and messaging.
               If not provided, a new Runner will be created.

    Raises:
        DependencyError: If Docker is not installed or the daemon is not running.
    """
    if runner is None:
        runner = Runner(dry_run=dry_run)

    runner.messages.info("Checking for required dependencies...")

    # 1. Check for Docker executable
    if not shutil.which("docker"):
        runner.messages.error("Docker is not installed or not in the system's PATH")
        raise DependencyError("Docker is not installed")
    runner.messages.info("Docker executable found")

    # 2. Check if Docker daemon is running (skip in dry-run)
    if runner.dry_run:
        runner.messages.info("DRY-RUN: Skipping Docker daemon check")
    else:

        def _check_daemon() -> None:
            try:
                subprocess.run(
                    ["docker", "info"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError as e:
                runner.messages.error("Docker daemon is not responding")
                runner.messages.info("Please start the Docker daemon and try again.")
                raise DependencyError("Docker daemon is not running.") from e
            except FileNotFoundError as e:
                # This case is technically covered by shutil.which, but included for robustness
                raise DependencyError(
                    "Docker command not found. Please ensure Docker is installed correctly."
                ) from e

        # Run the daemon check with a spinner
        runner.messages.with_spinner("Checking Docker daemon status", _check_daemon)
        runner.messages.info("Docker daemon is running")
