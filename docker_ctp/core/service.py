"""Service layer for core *docker-ctp* functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

from docker_ctp.core import docker_ops
from docker_ctp.exceptions import ConfigError
from docker_ctp.utils.build_context import validate_build_context
from docker_ctp.utils.input_validation import (
    validate_dockerfile_dir,
    validate_image_name,
    validate_tag,
    validate_username,
)

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
        """Run validation checks on user-provided inputs.

        Raises:
            ConfigError: If any validation check fails.
        """
        self.runner.messages.info("Validating configuration...")

        # Registry validation
        if self.config.registry not in {"docker", "github"}:
            raise ConfigError("Registry must be 'docker' or 'github'")

        # Credentials and Image Info validation
        self.runner.messages.info("Validating credentials and image info...")
        validate_username(self.config.username)
        validate_image_name(self.config.image_name)
        if self.config.tag:
            validate_tag(self.config.tag)

        # Dockerfile and Build Context validation
        self.runner.messages.info("Validating Dockerfile and build context...")
        validate_dockerfile_dir(self.config.dockerfile_dir)
        dockerfile_path = self.config.dockerfile_dir / "Dockerfile"
        if not dockerfile_path.is_file():
            raise ConfigError(f"Dockerfile not found at {dockerfile_path}")
        validate_build_context(self.config.dockerfile_dir)

        self.runner.messages.success("Configuration validation completed")

    def execute_workflow(self) -> None:
        """Execute the full build, tag, and push workflow.

        This method orchestrates the entire workflow, including validation,
        authentication, building, tagging, and pushing the Docker image.

        Raises:
            Exception: If any step in the workflow fails.
        """
        try:
            # Validate all inputs first
            self._validate_inputs()

            # Execute the workflow steps
            self.runner.messages.info("Executing workflow...")

            # Login to the registry
            docker_ops.login(self.config, self.runner)

            # Build the Docker image
            docker_ops.build(self.config, self.runner)

            # Tag the image with the registry prefix
            image = docker_ops.tag_image(self.config, self.runner)

            # Register the image for cleanup
            self.cleanup_manager.register(f"{self.config.image_name}:{self.config.tag}")

            # Push the image to the registry
            docker_ops.push(self.config, image, self.runner)

            self.runner.messages.success("Workflow completed successfully")

        except Exception as e:
            self.runner.messages.error(f"Workflow failed: {str(e)}")
            raise

        finally:
            # Always clean up if configured to do so
            if self.config.cleanup_on_exit:
                self.cleanup_manager.cleanup()
