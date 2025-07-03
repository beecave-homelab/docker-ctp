"""Cleanup utilities."""

from __future__ import annotations

import logging
import subprocess
from typing import List


class CleanupManager:
    """Manage cleanup of Docker images on exit."""

    def __init__(self, dry_run: bool) -> None:
        """Initialize the manager."""
        self.dry_run = dry_run
        self.images: List[str] = []

    def register(self, image: str) -> None:
        """Register an image for cleanup."""
        self.images.append(image)

    def cleanup(self) -> None:
        """Remove registered images."""
        if not self.images:
            return
        logging.info("Cleaning up intermediate images...")
        for image in self.images:
            if self.dry_run:
                logging.info("DRY-RUN would remove image %s", image)
                continue
            subprocess.run(
                ["docker", "rmi", image],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        logging.info("Cleanup completed")
