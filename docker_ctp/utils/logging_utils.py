"""Logging utilities with ASCII art and progress."""

from __future__ import annotations

import logging
import sys
import time
from typing import Any, Callable, TypeVar

from rich.console import Console

T = TypeVar("T")

ASCII_ART = """
d8888b.  .d88b.   .o88b. db   dD d88888b d8888b.                                 
88  `8D .8P  Y8. d8P  Y8 88 ,8P' 88'     88  `8D                                 
88   88 88    88 8P      88,8P   88ooooo 88oobY'                                 
88   88 88    88 8b      88`8b   88~~~~~ 88`8b                                   
88  .8D `8b  d8' Y8b  d8 88 `88. 88.     88 `88.                                 
Y8888D'  `Y88P'   `Y88P' YP   YD Y88888P 88   YD 
     
      Create, Tag and Push Docker images
"""


class MessageHandler:
    """Centralized message handling with consistent formatting using rich."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the message handler."""
        self.console = console or Console()

    def _should_show_info(self) -> bool:
        """Check if INFO level messages should be shown."""
        return logging.getLogger().level <= logging.INFO

    def success(self, message: str) -> None:
        """Display a success message with a checkmark at the start in green."""
        if self._should_show_info():
            self.console.print(f"[green]✓ {message}[/green]")

    def info(self, message: str) -> None:
        """Display an informational message."""
        if self._should_show_info():
            logging.info(message)

    def warning(self, message: str) -> None:
        """Display a warning message."""
        if self._should_show_info():
            logging.warning(message)

    def error(self, message: str) -> None:
        """Display an error message."""
        logging.error(message)

    def _flush_output_streams(self) -> None:
        """Ensure all output streams are flushed to prevent interleaving."""
        sys.stdout.flush()
        sys.stderr.flush()

    def with_spinner(
        self, text: str, operation: Callable[..., T], *args: Any, **kwargs: Any
    ) -> T:
        """Run an operation with a spinner.

        Args:
            text: The text to display next to the spinner
            operation: The operation to run
            *args: Positional arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            The result of the operation

        Raises:
            Exception: If the operation raises an exception
        """
        if not self._should_show_info():
            return operation(*args, **kwargs)

        text = text.rstrip(" ")
        with self.console.status(f"[cyan]{text}[/cyan]", spinner="dots") as _:
            try:
                self._flush_output_streams()
                time.sleep(0.1)
                self._flush_output_streams()
                result = operation(*args, **kwargs)
                self.success(text)
                return result
            except Exception:
                self.error(f"{text} failed")
                raise


def print_ascii_art(dry_run: bool) -> None:
    """Print ASCII art banner."""
    if logging.getLogger().level <= logging.INFO:
        console = Console()
        console.print(f"[cyan]{ASCII_ART}[/cyan]")
        if dry_run:
            console.print(
                "[bold yellow]DRY RUN MODE - No commands executed[/bold yellow]"
            )


def get_message_handler() -> MessageHandler:
    """Get a message handler instance."""
    return MessageHandler()


# For backward compatibility
progress = get_message_handler().info
