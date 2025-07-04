"""Cleanup utilities."""

from __future__ import annotations

import subprocess
from typing import List, Optional

from docker_ctp.core.runner import Runner


class CleanupManager:
    """Manage cleanup of Docker images on exit."""

    def __init__(self, dry_run: bool) -> None:
        """Initialize the manager.

        Args:
            dry_run: If True, no actual cleanup will be performed.
        """
        self.dry_run = dry_run
        self.images: List[str] = []
        self._runner: Optional[Runner] = None

    @property
    def runner(self) -> Runner:
        """Get or create a Runner instance."""
        if self._runner is None:
            self._runner = Runner(dry_run=self.dry_run)
        return self._runner

    def register(self, image: str) -> None:
        """Register an image for cleanup.

        Args:
            image: The name of the Docker image to clean up.
        """
        self.images.append(image)

    def cleanup(self) -> None:
        """Remove registered images."""
        if not self.images:
            return

        self.runner.messages.info("Cleaning up intermediate images...")

        for image in self.images:
            if self.dry_run:
                self.runner.messages.info(f"DRY-RUN would remove image {image}")
                continue

            try:
                self.runner.run(["docker", "rmi", image], text=f"Removing {image}")
            except subprocess.CalledProcessError:
                self.runner.messages.warning(f"Failed to remove image {image}")

        self.runner.messages.success("Cleanup completed")
