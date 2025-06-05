"""Docker operations used by docker-ctp."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from .config import Config
from .runner import Runner


def login(config: Config, runner: Runner) -> None:
    """Authenticate to the chosen registry."""
    logging.info("Logging into %s", config.registry)
    token_env = "DOCKER_TOKEN" if config.registry == "docker" else "GITHUB_TOKEN"
    token = os.environ.get(token_env)
    if not token:
        raise RuntimeError(f"Environment variable {token_env} not set")
    registry = "ghcr.io" if config.registry == "github" else None
    cmd = ["docker", "login"]
    if registry:
        cmd.append(registry)
    cmd.extend(["-u", config.username, "--password-stdin"])
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    if token:
        process.communicate(input=token.encode())
    if process.wait() != 0:
        raise RuntimeError("Failed to login")


def build(config: Config, runner: Runner) -> None:
    """Build the Docker image."""
    tag = f"{config.image_name}:{config.tag}"
    args = ["docker", "build", "-t", tag]
    if not config.use_cache:
        args.insert(2, "--no-cache")
    args.append(str(config.dockerfile_dir))
    runner.run(args)


def tag_image(config: Config, runner: Runner) -> str:
    """Tag the built Docker image."""
    source = f"{config.image_name}:{config.tag}"
    if config.registry == "docker":
        target = f"{config.docker_username}/{config.image_name}:{config.tag}"
    else:
        target = f"ghcr.io/{config.github_username}/{config.image_name}:{config.tag}"
    runner.run(["docker", "tag", source, target])
    return target


def push(config: Config, image: str, runner: Runner) -> None:
    """Push the tagged Docker image."""
    runner.run(["docker", "push", image])
