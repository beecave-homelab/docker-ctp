"""
Custom exception classes for the docker-ctp package.
"""

import click


class DockerCTPError(click.ClickException):
    """Base exception for all docker-ctp errors."""

    pass


class ConfigError(DockerCTPError):
    """Raised for configuration-related errors."""

    pass


class ValidationError(DockerCTPError):
    """Raised for input validation errors."""

    pass


class AuthError(DockerCTPError):
    """Raised for authentication or credential errors."""

    pass


class DependencyError(DockerCTPError):
    """Raised when required dependencies are missing or not running."""

    pass


class DockerOperationError(DockerCTPError):
    """Raised for errors during Docker operations (login, build, etc.)."""

    pass
