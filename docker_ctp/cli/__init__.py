"""Click-based command-line interface for *docker-ctp*.

This module exposes the :data:`cli` command (a *click* command object) which
mirrors the original Bash scriptʼs options while adding first-class
Python-native ergonomics such as:

* Type-checked parameters & sensible defaults.
* Rich validation prior to Docker calls.
* Full *dry-run* mode that performs zero network / Docker daemon actions.

Public attributes exported via :pydata:`__all__`:

* ``cli``  – Root *click* command for re-use by external tooling/tests.
* ``main`` – Entrypoint dispatched when executing ``python -m docker_ctp.cli``.
"""

from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

import click
from rich.console import Console
from rich.logging import RichHandler

from docker_ctp import __version__
from docker_ctp.config import DEFAULT_DOCKERFILE_DIR, DEFAULT_REGISTRY, Config, load_env
from docker_ctp.core.runner import Runner
from docker_ctp.core.service import DockerService
from docker_ctp.exceptions import CLIError
from docker_ctp.utils.cleanup import CleanupManager
from docker_ctp.utils.config_generation import generate_config_files
from docker_ctp.utils.dependency_checker import check_dependencies
from docker_ctp.utils.logging_utils import print_ascii_art


def configure_logging(verbose: bool, quiet: bool, console: Console) -> None:  # noqa: D401
    """Configure the root logger using rich."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True, show_path=False, show_time=False, console=console
            )
        ],
    )


# ---------------------------------------------------------------------------
# Helper functions for the new Click-powered CLI
# ---------------------------------------------------------------------------


def print_banner(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    """Print the ASCII art banner when the CLI is invoked.

    This is configured as a callback to ensure it runs before any command processing,
    including when --help is used.
    """
    if not value or ctx.resilient_parsing:
        return

    print_ascii_art(False)  # Pass False for dry_run to skip dry run message

    # Don't exit if this is just --help
    if not any(help_opt in sys.argv for help_opt in ("-h", "--help")):
        ctx.exit()


def build_cli() -> click.Command:  # noqa: D401
    """Construct the root *Click* command object.

    The returned command is assigned to the module-level :data:`cli` variable
    so it can be imported by third-party callers *without* re-building the
    option tree on every import (which speeds up test collection).
    """

    @click.command()
    @click.option(
        "--banner",
        is_flag=True,
        is_eager=True,
        expose_value=False,
        callback=print_banner,
        help="Show the ASCII art banner and exit",
    )
    @click.option("-u", "--username", help="Registry username")
    @click.option("-i", "--image-name", help="Docker image name")
    @click.option("-t", "--image-tag", "tag", help="Docker image tag")
    @click.option(
        "-d",
        "--dockerfile-dir",
        type=click.Path(path_type=Path, file_okay=False, dir_okay=True, exists=False),
        default=str(DEFAULT_DOCKERFILE_DIR),
        help="Path to Dockerfile directory",
    )
    @click.option(
        "-g",
        "--registry",
        type=click.Choice(["docker", "github"]),
        default=DEFAULT_REGISTRY,
        help="Target registry",
    )
    @click.option(
        "--no-cache",
        is_flag=True,
        help="Disable build cache",
    )
    @click.option(
        "--force-rebuild", is_flag=True, help="Force rebuild even if image exists"
    )
    @click.option("--dry-run", is_flag=True, help="Simulate commands without executing")
    @click.option("--verbose", is_flag=True, help="Verbose output")
    @click.option("--quiet", is_flag=True, help="Suppress output")
    @click.option("--no-cleanup", is_flag=True, help="Disable cleanup of images")
    @click.option(
        "--generate-config",
        is_flag=True,
        help="Generate default configuration files and exit",
    )
    @click.version_option(__version__, "--version", prog_name="docker-ctp")
    def main_command(  # noqa: D401
        **kwargs,
    ) -> None:
        """Entry-point for *docker-ctp* when invoked via the CLI."""
        console = Console(force_terminal=True)
        configure_logging(kwargs["verbose"], kwargs["quiet"], console)

        # Only print ASCII art again if we're not in quiet mode and this isn't a help request
        if not kwargs["quiet"] and not any(
            help_opt in sys.argv for help_opt in ("-h", "--help")
        ):
            print_ascii_art(kwargs["dry_run"])

        if kwargs["generate_config"]:
            generate_config_files(kwargs["dry_run"])
            return

        # Create a Config instance from the parsed CLI arguments.
        args = SimpleNamespace(**kwargs)
        config = Config.from_cli(args)

        load_env(config)
        config.resolve()

        runner = Runner(dry_run=config.dry_run, console=console)
        cleanup_manager = CleanupManager(dry_run=config.dry_run)

        # Check dependencies after creating the runner
        check_dependencies(runner)

        service = DockerService(
            config=config, runner=runner, cleanup_manager=cleanup_manager
        )
        service.execute_workflow()

        # Emit a simple completion message for CLI tests
        # Ensure the final completion text is always printed for tests
        click.echo("Completed")

    return main_command


# Build the command on import so external callers can re-use it.
cli = build_cli()


def format_click_error(error: Exception) -> str:
    """Format Click exceptions into user-friendly error messages.

    Args:
        error: The exception to format

    Returns:
        str: A user-friendly error message
    """
    if isinstance(error, click.NoSuchOption):
        return f"Error: Unknown option: {error.option_name}"
    if isinstance(error, click.UsageError):
        return f"Error: {error.format_message()}"
    if isinstance(error, click.BadParameter):
        return f"Error: {error.format_message()}"
    return f"Error: {str(error)}"


def main() -> int:  # noqa: D401
    """Dispatch execution to :data:`cli` when ``python -m docker_ctp.cli`` runs.

    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        return cli.main(prog_name="docker-ctp", standalone_mode=True)
    except CLIError as e:
        # Handle our custom CLI errors first (more specific)
        click.echo(e.format_message(), err=True)
        return 1
    except click.ClickException as e:
        # Handle Click-specific exceptions
        click.echo(format_click_error(e), err=True)
        return e.exit_code
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Handle unexpected errors
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)
        if "--verbose" in sys.argv or "-v" in sys.argv:
            traceback.print_exc()
        return 1


if __name__ == "__main__":  # pragma: no cover
    main()

# ---------------------------------------------------------------------------
# Public re-exports (documented in the module docstring)
# ---------------------------------------------------------------------------

__all__: list[str] = [
    "cli",
    "main",
]
