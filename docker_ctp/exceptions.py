"""
Custom exception classes for the docker-ctp package.
"""

import click


class DockerCTPError(click.ClickException):
    """Base exception for all docker-ctp errors."""


class ConfigError(DockerCTPError):
    """Raised for configuration-related errors."""


class ValidationError(DockerCTPError):
    """Raised for input validation errors."""


class AuthError(DockerCTPError):
    """Raised for authentication or credential errors."""


class DependencyError(DockerCTPError):
    """Raised when required dependencies are missing or not running."""


class DockerOperationError(DockerCTPError):
    """Raised for errors during Docker operations (login, build, etc.)."""
