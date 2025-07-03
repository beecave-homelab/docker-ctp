"""Dependency checking utilities."""

from __future__ import annotations

import logging
import shutil
import subprocess

from docker_ctp.exceptions import DependencyError


__all__: list[str] = [
    "check_dependencies",
]


def check_dependencies(dry_run: bool) -> None:  # noqa: D401
    """Verify that Docker is installed and the daemon is running."""
    logging.info("Checking for required dependencies...")

    # 1. Check for Docker executable
    if not shutil.which("docker"):
        raise DependencyError(
            "Docker is not installed or not in the system's PATH. "
            "Please install Docker and try again."
        )
    logging.info("✓ Docker executable found.")

    # 2. Check if Docker daemon is running (skip in dry-run)
    if dry_run:
        logging.info("DRY-RUN: Skipping Docker daemon check.")
        return

    logging.info("Checking Docker daemon status...")
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logging.info("✓ Docker daemon is running.")
    except subprocess.CalledProcessError as e:
        logging.error("Docker daemon is not responding.")
        logging.info("Please start the Docker daemon and try again.")
        raise DependencyError("Docker daemon is not running.") from e
    except FileNotFoundError as e:
        # This case is technically covered by shutil.which, but included for robustness
        raise DependencyError(
            "Docker command not found. Please ensure Docker is installed."
        ) from e
