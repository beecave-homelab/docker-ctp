"""Configuration management for docker-ctp."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DOCKER_USERNAME = os.environ.get("USER", "")
DEFAULT_GITHUB_USERNAME = os.environ.get("USER", "")
DEFAULT_IMAGE_NAME = Path.cwd().name
DEFAULT_DOCKERFILE_DIR = Path(".")
DEFAULT_REGISTRY = "docker"
DEFAULT_DOCKERHUB_TAG = "latest"
DEFAULT_GITHUB_TAG = "main"


@dataclass
class Config:
    """Configuration values for docker-ctp."""

    registry: str = DEFAULT_REGISTRY
    docker_username: str = DEFAULT_DOCKER_USERNAME
    github_username: str = DEFAULT_GITHUB_USERNAME
    username: str = ""
    image_name: str = DEFAULT_IMAGE_NAME
    tag: str | None = None
    dockerfile_dir: Path = DEFAULT_DOCKERFILE_DIR
    use_cache: bool = True
    force_rebuild: bool = False
    dry_run: bool = False
    log_level: str = "normal"
    cleanup_on_exit: bool = True

    def resolve_username(self) -> None:
        if not self.username:
            self.username = (
                self.docker_username
                if self.registry == "docker"
                else self.github_username
            )

    def set_default_tag(self) -> None:
        if not self.tag:
            self.tag = (
                DEFAULT_DOCKERHUB_TAG
                if self.registry == "docker"
                else DEFAULT_GITHUB_TAG
            )


ENV_LOCATIONS = [
    Path(".env"),
    Path.home() / ".config" / "docker-ctp" / ".env",
    Path.home() / ".docker-ctp" / ".env",
    Path("/etc/docker-ctp/.env"),
]


def load_env(config: Config) -> None:
    """Load configuration from environment files."""
    for location in ENV_LOCATIONS:
        if location.is_file():
            logging.info("Loading configuration from %s", location)
            with location.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)
            break

    config.docker_username = os.environ.get("DOCKER_USERNAME", config.docker_username)
    config.github_username = os.environ.get("GITHUB_USERNAME", config.github_username)
    config.image_name = os.environ.get("IMAGE_NAME", config.image_name)
    config.dockerfile_dir = Path(
        os.environ.get("DOCKERFILE_DIR", str(config.dockerfile_dir))
    )
    config.registry = os.environ.get("REGISTRY", config.registry)
    if os.environ.get("NO_CLEANUP"):
        config.cleanup_on_exit = False


def validate_config(config: Config) -> None:
    """Validate a Config instance."""
    if config.registry not in {"docker", "github"}:
        raise ValueError("Registry must be 'docker' or 'github'")
    if not config.username:
        raise ValueError("Username is required")
    if not config.image_name:
        raise ValueError("Image name is required")
    dockerfile = config.dockerfile_dir / "Dockerfile"
    if not dockerfile.is_file():
        raise FileNotFoundError(f"Dockerfile not found at {dockerfile}")
