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

import subprocess

from docker_ctp.config import Config
from docker_ctp.core.runner import Runner
from docker_ctp.exceptions import DockerOperationError
from docker_ctp.utils.auth import get_token
from docker_ctp.utils.rebuild import image_exists


def login(config: Config, runner: Runner) -> None:
    """Authenticate the Docker CLI to the target registry.

    Args:
        config: Active runtime configuration.
        runner: Command runner controlling *dry-run* behaviour.

    Raises:
        DockerOperationError: If the underlying ``docker login`` command exits with a
            non-zero status *and* we are **not** in dry-run mode.
    """
    runner.messages.info(f"Logging into {config.registry}")

    # Short-circuit when running in *dry-run* mode so that unit tests and
    # CI pipelines can execute without requiring access to Docker Hub or
    # GitHub Container Registry.  The rest of the pipeline will still run
    # but no network calls or credential prompts will occur.
    if runner.dry_run:
        runner.messages.info("DRY-RUN: skipping docker login")
        return

    def _perform_login() -> None:
        runner.messages.info("Attempting to get token for registry: %s", config.registry)
        token = get_token(config.registry)

        if not token:
            runner.messages.error("Authentication token not found.")
            raise DockerOperationError(
                f"No token found for {config.registry}. "
                "Please set DOCKER_HUB_TOKEN/GITHUB_TOKEN or log in manually."
            )
        runner.messages.info("Token found, proceeding with login for user: %s", config.username)

        registry = "ghcr.io" if config.registry == "github" else None
        cmd = ["docker", "login"]
        if registry:
            cmd.append(registry)
        cmd.extend(["-u", config.username, "--password-stdin"])
        runner.messages.info("Executing command: %s", " ".join(cmd))

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        runner.messages.info("Waiting for docker login process to complete...")
        stdout, stderr = process.communicate(input=token.encode())
        runner.messages.info("Process finished with return code: %s", process.returncode)

        if stdout:
            runner.messages.info("STDOUT: %s", stdout.decode().strip())
        if stderr:
            runner.messages.info("STDERR: %s", stderr.decode().strip())

        if process.returncode != 0:
            error_message = stderr.decode().strip() or stdout.decode().strip()
            raise DockerOperationError(f"Failed to login: {error_message}")

    _perform_login()
    runner.messages.success("Successfully authenticated with registry")


def build(config: Config, runner: Runner) -> None:
    """Build a Docker image from *config.dockerfile_dir*.

    Args:
        config: Validated configuration.
        runner: Command runner controlling *dry-run* behaviour.
    """
    tag = f"{config.image_name}:{config.tag}"
    if not config.force_rebuild and image_exists(tag):
        runner.messages.info(f"Image {tag} already exists - skipping build")
        return

    runner.messages.info(f"Building Docker image: {tag}")
    args = ["docker", "build", "-t", tag]
    if not config.use_cache:
        args.insert(2, "--no-cache")
    args.append(str(config.dockerfile_dir))
    runner.run(args, text=f"Building {tag}")


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

    runner.messages.info(f"Tagging image as {target}")
    runner.run(["docker", "tag", source, target], text=f"Tagging {source}")
    return target


def push(config: Config, image: str, runner: Runner) -> None:
    """Push a local Docker image to its remote registry.

    Args:
        config: Validated configuration.
        image: The image to push (including tag).
        runner: Command runner controlling *dry-run* behaviour.
    """
    runner.messages.info(f"Pushing {image} to {config.registry}")
    runner.run(["docker", "push", image], text=f"Pushing {image}")


# ---------------------------------------------------------------------------
# Public re-exports
# ---------------------------------------------------------------------------

__all__: list[str] = [
    "login",
    "build",
    "tag_image",
    "push",
]
