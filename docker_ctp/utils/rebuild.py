"""Smart rebuild utilities."""

from __future__ import annotations

import subprocess


def image_exists(tag: str) -> bool:
    """Return True if Docker image with given tag already exists."""
    result = subprocess.run(
        ["docker", "image", "inspect", tag],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0
