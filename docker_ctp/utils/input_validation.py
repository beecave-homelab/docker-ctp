"""Input validation utilities."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from docker_ctp.exceptions import ValidationError

logger = logging.getLogger(__name__)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{1,100}$")
IMAGE_RE = re.compile(r"^[a-zA-Z0-9._-]{1,100}$")
TAG_RE = re.compile(r"^[a-zA-Z0-9._-]{1,100}$")


def validate_username(username: str) -> None:
    """Validate registry username."""
    if not USERNAME_RE.match(username):
        raise ValidationError(f"Invalid username: {username}")


def validate_image_name(name: str) -> None:
    """Validate image name."""
    if not IMAGE_RE.match(name):
        raise ValidationError(f"Invalid image name: {name}")


def validate_tag(tag: str) -> None:
    """Validate image tag."""
    if not TAG_RE.match(tag):
        raise ValidationError(f"Invalid tag: {tag}")


def validate_dockerfile_dir(path: Path) -> None:
    """Ensure Dockerfile exists in the directory."""
    logger.debug("Checking for Dockerfile at %s", path / "Dockerfile")
    if not path.is_dir():
        raise ValidationError(f"Dockerfile directory not found: {path}")
    dockerfile = path / "Dockerfile"
    if not dockerfile.is_file():
        logger.debug("Dockerfile not found at %s", dockerfile)
        raise ValidationError(f"Dockerfile not found at {dockerfile}")
