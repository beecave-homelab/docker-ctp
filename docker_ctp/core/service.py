"""Service layer for core *docker-ctp* functionality."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import click

from ..core import docker_ops
from ..utils.build_context import validate_build_context
from ..utils.input_validation import (
    validate_dockerfile_dir,
    validate_image_name,
    validate_tag,
    validate_username,
)

if TYPE_CHECKING:
    from ..config import Config
    from ..core.runner import Runner
    from ..utils.cleanup import CleanupManager


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
        validate_username(self.config.username)
        validate_image_name(self.config.image_name)
        if self.config.tag:
            validate_tag(self.config.tag)
        validate_dockerfile_dir(self.config.dockerfile_dir)
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