"""Configuration file generation utilities."""

from __future__ import annotations

import logging
from pathlib import Path

ENV_TEMPLATE = """# Docker CTP Configuration File
DOCKER_USERNAME=your-dockerhub-username
GITHUB_USERNAME=your-github-username
DOCKERFILE_DIR=.
REGISTRY=docker
"""

DOCKERIGNORE_TEMPLATE = """# Docker CTP - Dockerignore Template
.git
*.log
node_modules/
"""


def generate_config_files() -> None:
    """Generate default .env and .dockerignore files."""
    env_path = Path.home() / ".config" / "docker-ctp" / ".env"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if not env_path.exists():
        env_path.write_text(ENV_TEMPLATE, encoding="utf-8")
        logging.info("Generated: %s", env_path)
    else:
        logging.info("Configuration file already exists: %s", env_path)

    dockerignore = Path(".dockerignore")
    if not dockerignore.exists():
        dockerignore.write_text(DOCKERIGNORE_TEMPLATE, encoding="utf-8")
        logging.info("Generated: %s", dockerignore)
    else:
        logging.info(".dockerignore already exists - skipping template generation")
