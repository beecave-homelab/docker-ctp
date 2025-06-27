"""High-level Docker operations used by *docker-ctp*.

The functions in this module are thin wrappers around the Docker CLI. They are
purposely *free of side-effects* other than spawning subprocesses; all
user-facing validation happens in :pymod:`docker_ctp.utils.*`.

Public API exported via :data:`__all__`:

* ``login`` – Authenticate to Docker Hub or GHCR.
* ``build`` – Build an image from a Dockerfile.
* ``tag_image`` – Add a registry-qualified tag to a local image.
* ``push`` – Push the tagged image to the remote registry.
"""

from __future__ import annotations

import logging
import subprocess

from ..config import Config
from ..utils.auth import get_token
from ..utils.rebuild import image_exists
from .runner import Runner
from ..exceptions import DockerOperationError


def login(config: Config, runner: Runner) -> None:
    """Authenticate the Docker CLI to the target registry.

    Args:
        config: Active runtime configuration.
        runner: Command runner controlling *dry-run* behaviour.

    Raises:
        DockerOperationError: If the underlying ``docker login`` command exits with a
            non-zero status *and* we are **not** in dry-run mode.
    """
    logging.info("Logging into %s", config.registry)

    # Short-circuit when running in *dry-run* mode so that unit tests and
    # CI pipelines can execute without requiring access to Docker Hub or
    # GitHub Container Registry.  The rest of the pipeline will still run
    # but no network calls or credential prompts will occur.
    if runner.dry_run:
        logging.info("DRY-RUN: skipping docker login")
        return

    token = get_token(config.registry)
    registry = "ghcr.io" if config.registry == "github" else None
    cmd = ["docker", "login"]
    if registry:
        cmd.append(registry)
    cmd.extend(["-u", config.username, "--password-stdin"])
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    if token:
        process.communicate(input=token.encode())
    if process.wait() != 0:
        raise DockerOperationError("Failed to login")


def build(config: Config, runner: Runner) -> None:
    """Build a Docker image from *config.dockerfile_dir*.

    Args:
        config: Validated configuration.
        runner: Command runner controlling *dry-run* behaviour.
    """
    tag = f"{config.image_name}:{config.tag}"
    if not config.force_rebuild and image_exists(tag):
        logging.info("Image %s already exists - skipping build", tag)
        return

    args = ["docker", "build", "-t", tag]
    if not config.use_cache:
        args.insert(2, "--no-cache")
    args.append(str(config.dockerfile_dir))
    runner.run(args)


def tag_image(config: Config, runner: Runner) -> str:
    """Apply a registry-qualified tag to the freshly built image.

    Args:
        config: Validated configuration.
        runner: Command runner controlling *dry-run* behaviour.

    Returns:
        The full name of the newly tagged image.
    """
    source = f"{config.image_name}:{config.tag}"
    if config.registry == "docker":
        target = f"{config.docker_username}/{config.image_name}:{config.tag}"
    else:
        target = f"ghcr.io/{config.github_username}/{config.image_name}:{config.tag}"
    runner.run(["docker", "tag", source, target])
    return target


def push(config: Config, image: str, runner: Runner) -> None:
    """Push a local Docker image to its remote registry."""
    runner.run(["docker", "push", image])


# ---------------------------------------------------------------------------
# Public re-exports
# ---------------------------------------------------------------------------

__all__: list[str] = [
    "login",
    "build",
    "tag_image",
    "push",
]
