"""Command line interface for docker-ctp."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from . import __version__
from .config import (DEFAULT_DOCKERFILE_DIR, DEFAULT_IMAGE_NAME,
                     DEFAULT_REGISTRY, Config, load_env, validate_config)
from .docker_ops import build, login, push, tag_image
from .modules.build_context import validate_build_context
from .modules.cleanup import CleanupManager
from .modules.config_generation import generate_config_files
from .modules.dependency_checker import check_dependencies
from .modules.input_validation import (validate_dockerfile_dir,
                                       validate_image_name, validate_tag,
                                       validate_username)
from .modules.logging_utils import print_ascii_art
from .runner import Runner


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Build and push Docker images")
    parser.add_argument("-u", "--username", help="Registry username")
    parser.add_argument("-i", "--image-name", help="Docker image name")
    parser.add_argument("-t", "--image-tag", dest="tag", help="Docker image tag")
    parser.add_argument(
        "-d",
        "--dockerfile-dir",
        default=str(DEFAULT_DOCKERFILE_DIR),
        help="Path to Dockerfile directory",
    )
    parser.add_argument(
        "-g",
        "--registry",
        choices=["docker", "github"],
        default=DEFAULT_REGISTRY,
        help="Target registry",
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable build cache")
    parser.add_argument("--force-rebuild", action="store_true", help="Force rebuild")
    parser.add_argument("--dry-run", action="store_true", help="Simulate commands")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    parser.add_argument(
        "--no-cleanup", action="store_true", help="Disable cleanup of images"
    )
    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate default configuration files and exit",
    )
    parser.add_argument(
        "--version", action="version", version=f"docker-ctp {__version__}"
    )
    return parser.parse_args()


def configure_logging(args: argparse.Namespace) -> None:
    """Configure logging level based on CLI flags."""
    if args.quiet:
        level = logging.ERROR
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)


def main() -> None:
    """Entry point for the CLI."""
    args = parse_args()
    configure_logging(args)
    print_ascii_art(args.dry_run)

    if args.generate_config:
        generate_config_files()
        return

    check_dependencies(args.dry_run)
    config = Config(
        registry=args.registry,
        username=args.username or "",
        image_name=args.image_name or DEFAULT_IMAGE_NAME,
        tag=args.tag,
        dockerfile_dir=Path(args.dockerfile_dir),
        use_cache=not args.no_cache,
        force_rebuild=args.force_rebuild,
        dry_run=args.dry_run,
        cleanup_on_exit=not args.no_cleanup,
    )
    load_env(config)
    config.resolve_username()
    config.set_default_tag()
    validate_config(config)

    validate_username(config.username)
    validate_image_name(config.image_name)
    if config.tag:
        validate_tag(config.tag)
    validate_dockerfile_dir(config.dockerfile_dir)
    validate_build_context(config.dockerfile_dir)

    runner = Runner(dry_run=config.dry_run)
    cleanup_mgr = CleanupManager(config.dry_run)
    try:
        login(config, runner)
        build(config, runner)
        image = tag_image(config, runner)
        cleanup_mgr.register(f"{config.image_name}:{config.tag}")
        push(config, image, runner)
        logging.info("Completed")
    finally:
        if config.cleanup_on_exit:
            cleanup_mgr.cleanup()


if __name__ == "__main__":  # pragma: no cover
    main()
