"""Service layer for core *docker-ctp* functionality."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import click

from docker_ctp.core import docker_ops
from docker_ctp.utils.build_context import validate_build_context
from docker_ctp.utils.input_validation import (
    validate_dockerfile_dir,
    validate_image_name,
    validate_tag,
    validate_username,
)
from ..exceptions import ConfigError

if TYPE_CHECKING:
    from docker_ctp.config import Config
    from docker_ctp.core.runner import Runner
    from docker_ctp.utils.cleanup import CleanupManager


class DockerService:
    """Orchestrates the main build-tag-push workflow.

    This service encapsulates the core business logic of the application,
    decoupling it from the CLI. It relies on dependency injection for its
    components (`Config`, `Runner`, `CleanupManager`), which makes it easy
    to test and configure.
    """

    def __init__(
        self,
        config: Config,
        runner: Runner,
        cleanup_manager: CleanupManager,
    ) -> None:
        """Initialize the service with its dependencies.

        Args:
            config: The application's runtime configuration.
            runner: The command runner for executing Docker commands.
            cleanup_manager: The manager for cleaning up Docker images.

        """
        self.config = config
        self.runner = runner
        self.cleanup_manager = cleanup_manager

    def _validate_inputs(self) -> None:
        """Run validation checks on user-provided inputs."""
        logging.info("Validating configuration...")
        # Registry
        if self.config.registry not in {"docker", "github"}:
            raise ConfigError("Registry must be 'docker' or 'github'")

        # Credentials and Image Info
        validate_username(self.config.username)
        validate_image_name(self.config.image_name)
        if self.config.tag:
            validate_tag(self.config.tag)

        # Dockerfile and Build Context
        validate_dockerfile_dir(self.config.dockerfile_dir)
        dockerfile_path = self.config.dockerfile_dir / "Dockerfile"
        if not dockerfile_path.is_file():
            raise ConfigError(f"Dockerfile not found at {dockerfile_path}")
        validate_build_context(self.config.dockerfile_dir)

    def execute_workflow(self) -> None:
        """Execute the full build, tag, and push workflow."""
        self._validate_inputs()

        try:
            docker_ops.login(self.config, self.runner)
            docker_ops.build(self.config, self.runner)
            image = docker_ops.tag_image(self.config, self.runner)
            self.cleanup_manager.register(f"{self.config.image_name}:{self.config.tag}")
            docker_ops.push(self.config, image, self.runner)
            logging.info("Completed")
        finally:
            if self.config.cleanup_on_exit:
                self.cleanup_manager.cleanup()

        click.echo("Completed")
