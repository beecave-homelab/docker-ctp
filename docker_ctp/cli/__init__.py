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
from types import SimpleNamespace
from pathlib import Path

import click

from .. import __version__
from ..config import (
    DEFAULT_DOCKERFILE_DIR,
    DEFAULT_REGISTRY,
    Config,
    load_env,
    validate_config,
)
from ..core.runner import Runner
from ..core.service import DockerService
from ..utils.build_context import validate_build_context
from ..utils.cleanup import CleanupManager
from ..utils.config_generation import generate_config_files
from ..utils.dependency_checker import check_dependencies
from ..utils.input_validation import (
    validate_dockerfile_dir,
    validate_image_name,
    validate_tag,
    validate_username,
)
from ..utils.logging_utils import print_ascii_art


def configure_logging(verbose: bool, quiet: bool) -> None:  # noqa: D401
    """Configure the root logger.

    Args:
        verbose: When *True* set the log-level to :pydata:`logging.DEBUG`.
        quiet:   When *True* silence all info/debug output (ERROR only).

    Notes:
        The flags are mutually exclusive; *quiet* wins over *verbose* when
        both are provided (mirroring many CLI conventions).
    """
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)


# ---------------------------------------------------------------------------
# Helper functions for the new Click-powered CLI
# ---------------------------------------------------------------------------


def create_config_from_ctx(ctx: click.Context) -> Config:  # noqa: D401
    """Convert Click context parameters into a :class:`docker_ctp.config.Config`.

    Args:
        ctx: The active Click context containing parsed command-line values.

    Returns:
        A fully populated :class:`docker_ctp.config.Config` instance ready for
        environment overrides and validation.
    """
    p = ctx.params  # shorthand
    args_ns = SimpleNamespace(
        registry=p["registry"],
        username=p.get("username"),
        image_name=p.get("image_name"),
        tag=p.get("tag"),
        dockerfile_dir=str(p.get("dockerfile_dir")),
        no_cache=p.get("no_cache"),
        force_rebuild=p.get("force_rebuild"),
        dry_run=p.get("dry_run"),
        verbose=p.get("verbose"),
        quiet=p.get("quiet"),
        no_cleanup=p.get("no_cleanup"),
    )
    return Config.from_cli(args_ns)


def build_cli() -> click.Command:  # noqa: D401
    """Construct the root *Click* command object.

    The returned command is assigned to the module-level :data:`cli` variable
    so it can be imported by third-party callers *without* re-building the
    option tree on every import (which speeds up test collection).
    """

    @click.command()
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
    @click.option("--no-cache", is_flag=True, help="Disable build cache")
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
    @click.pass_context
    def cli(
        ctx: click.Context,
        username: str | None,
        image_name: str | None,
        tag: str | None,
        dockerfile_dir: Path,
        registry: str,
        no_cache: bool,
        force_rebuild: bool,
        dry_run: bool,
        verbose: bool,
        quiet: bool,
        no_cleanup: bool,
        generate_config: bool,
    ) -> None:  # noqa: D401
        """Entry-point for *docker-ctp* when invoked via the CLI."""
        print(f"DEBUG: cli received dockerfile_dir={dockerfile_dir}")
        configure_logging(verbose, quiet)
        print_ascii_art(dry_run)

        if generate_config:
            generate_config_files()
            return

        check_dependencies(dry_run)

        # Store parameters on the context so sub-commands (if added later) can access.
        ctx.params.update(
            {
                "username": username,
                "image_name": image_name,
                "tag": tag,
                "dockerfile_dir": dockerfile_dir,
                "registry": registry,
                "no_cache": no_cache,
                "force_rebuild": force_rebuild,
                "dry_run": dry_run,
                "verbose": verbose,
                "quiet": quiet,
                "no_cleanup": no_cleanup,
            }
        )

        config = create_config_from_ctx(ctx)
        load_env(config)
        config.resolve()

        runner = Runner(dry_run=config.dry_run)
        cleanup_manager = CleanupManager(dry_run=config.dry_run)
        service = DockerService(
            config=config, runner=runner, cleanup_manager=cleanup_manager
        )
        service.execute_workflow()

    return cli


# Build the command on import so external callers can re-use it.
cli = build_cli()


def main() -> None:  # noqa: D401
    """Dispatch execution to :data:`cli` when ``python -m docker_ctp.cli`` runs."""
    cli.main(prog_name="docker-ctp", standalone_mode=False)


if __name__ == "__main__":  # pragma: no cover
    main()

# ---------------------------------------------------------------------------
# Public re-exports (documented in the module docstring)
# ---------------------------------------------------------------------------

__all__: list[str] = [
    "cli",
    "main",
]
