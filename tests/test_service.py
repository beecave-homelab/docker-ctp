"""Unit tests for the DockerService."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from docker_ctp.config import Config
from docker_ctp.core.service import DockerService


@pytest.fixture
def _mock_config() -> Config:
    """Provide a mock Config object."""
    return MagicMock(spec=Config)


@pytest.fixture
def _mock_runner() -> MagicMock:
    """Provide a mock Runner object."""
    return MagicMock()


@pytest.fixture
def _mock_cleanup_manager() -> MagicMock:
    """Provide a mock CleanupManager object."""
    return MagicMock()


@patch("docker_ctp.core.service.validate_username")
@patch("docker_ctp.core.service.validate_image_name")
@patch("docker_ctp.core.service.validate_tag")
@patch("docker_ctp.core.service.validate_dockerfile_dir")
@patch("docker_ctp.core.service.validate_build_context")
@patch("docker_ctp.core.service.docker_ops")
def test_execute_workflow(
    mock_docker_ops: MagicMock,
    mock_validate_build_context: MagicMock,
    mock_validate_dockerfile_dir: MagicMock,
    mock_validate_tag: MagicMock,
    mock_validate_image_name: MagicMock,
    mock_validate_username: MagicMock,
    _mock_config: Config,
    _mock_runner: MagicMock,
    _mock_cleanup_manager: MagicMock,
):
    """Test the main workflow execution."""
    # Arrange
    service = DockerService(_mock_config, _mock_runner, _mock_cleanup_manager)
    _mock_config.registry = "docker"
    _mock_config.tag = "latest"
    _mock_config.image_name = "test-image"
    _mock_config.cleanup_on_exit = True
    mock_docker_ops.tag_image.return_value = "registry/test-image:latest"

    # Act
    service.execute_workflow()

    # Assert
    # Validation calls
    mock_validate_username.assert_called_once_with(_mock_config.username)
    mock_validate_image_name.assert_called_once_with(_mock_config.image_name)
    mock_validate_tag.assert_called_once_with(_mock_config.tag)
    mock_validate_dockerfile_dir.assert_called_once_with(_mock_config.dockerfile_dir)
    mock_validate_build_context.assert_called_once_with(_mock_config.dockerfile_dir)

    # Docker operations calls
    mock_docker_ops.login.assert_called_once_with(_mock_config, _mock_runner)
    mock_docker_ops.build.assert_called_once_with(_mock_config, _mock_runner)
    mock_docker_ops.tag_image.assert_called_once_with(_mock_config, _mock_runner)
    mock_docker_ops.push.assert_called_once_with(
        _mock_config, "registry/test-image:latest", _mock_runner
    )

    # Cleanup manager calls
    _mock_cleanup_manager.register.assert_called_once_with("test-image:latest")
    _mock_cleanup_manager.cleanup.assert_called_once()
