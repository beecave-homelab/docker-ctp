"""Custom exception classes for the docker-ctp package."""

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


class CLIError(DockerCTPError):
    """Raised for command-line interface related errors."""

    def __init__(self, message, ctx=None, help_message=None):
        super().__init__(message)
        self.ctx = ctx
        self.help_message = help_message or ""

    def format_message(self):
        if self.help_message:
            return f"{self.message}\n\n{self.help_message}"
        return self.message
