"""Configuration management for docker-ctp."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from ..exceptions import ConfigError

DEFAULT_DOCKER_USERNAME = os.environ.get("USER", "")
DEFAULT_GITHUB_USERNAME = os.environ.get("USER", "")
DEFAULT_IMAGE_NAME = Path.cwd().name
DEFAULT_DOCKERFILE_DIR = Path(".")
DEFAULT_REGISTRY = "docker"
DEFAULT_DOCKERHUB_TAG = "latest"
DEFAULT_GITHUB_TAG = "main"


@dataclass
class RegistryCredentials:
    """Registry-related settings and user information."""

    registry: str = DEFAULT_REGISTRY
    docker_username: str = DEFAULT_DOCKER_USERNAME
    github_username: str = DEFAULT_GITHUB_USERNAME
    username: str = ""

    def resolve_username(self) -> None:
        """Populate *username* using the registry-specific defaults when empty."""
        if not self.username:
            self.username = (
                self.docker_username
                if self.registry == "docker"
                else self.github_username
            )


@dataclass
class ImageInfo:
    """Container image information (name, tag, Dockerfile path)."""

    image_name: str = DEFAULT_IMAGE_NAME
    tag: str | None = None
    dockerfile_dir: Path = DEFAULT_DOCKERFILE_DIR

    def set_default_tag(self, registry: str) -> None:
        """Fill in a sensible default tag when none is provided."""
        if not self.tag:
            self.tag = (
                DEFAULT_DOCKERHUB_TAG if registry == "docker" else DEFAULT_GITHUB_TAG
            )


@dataclass
class BuildFlags:
    """Flags that influence the *docker build* command."""

    use_cache: bool = True
    force_rebuild: bool = False


@dataclass
class RuntimeFlags:
    """General runtime/UX flags that don't affect the resulting image."""

    dry_run: bool = False
    log_level: str = "normal"
    cleanup_on_exit: bool = True


@dataclass
class Config:
    """Aggregate of all configuration domains.

    Backwards-compatibility helpers expose the original attribute names so that
    existing code can continue to use *config.registry*, *config.image_name*,
    and friends without alteration. New code should prefer the namespaced
    dataclasses stored in *creds*, *image*, *build*, and *runtime*.
    """

    creds: RegistryCredentials = field(default_factory=RegistryCredentials)
    image: ImageInfo = field(default_factory=ImageInfo)
    build: BuildFlags = field(default_factory=BuildFlags)
    runtime: RuntimeFlags = field(default_factory=RuntimeFlags)

    # ---------------------------------------------------------------------
    # Constructors
    # ---------------------------------------------------------------------

    @classmethod
    def from_cli(cls, args: SimpleNamespace) -> "Config":
        """Create a Config instance directly from parsed CLI *args*."""
        creds = RegistryCredentials(
            registry=args.registry, username=args.username or ""
        )
        image = ImageInfo(
            image_name=args.image_name or DEFAULT_IMAGE_NAME,
            tag=args.tag,
            dockerfile_dir=Path(args.dockerfile_dir),
        )
        build = BuildFlags(
            use_cache=not args.no_cache, force_rebuild=args.force_rebuild
        )
        runtime = RuntimeFlags(
            dry_run=args.dry_run,
            log_level="verbose"
            if args.verbose
            else "quiet"
            if args.quiet
            else "normal",
            cleanup_on_exit=not args.no_cleanup,
        )
        return cls(creds=creds, image=image, build=build, runtime=runtime)

    @classmethod
    def from_env(cls) -> "Config":
        """Create a Config instance solely from environment variables."""
        creds = RegistryCredentials(
            registry=os.environ.get("REGISTRY", DEFAULT_REGISTRY),
            docker_username=os.environ.get("DOCKER_USERNAME", DEFAULT_DOCKER_USERNAME),
            github_username=os.environ.get("GITHUB_USERNAME", DEFAULT_GITHUB_USERNAME),
            username=os.environ.get("USERNAME", ""),
        )
        image = ImageInfo(
            image_name=os.environ.get("IMAGE_NAME", DEFAULT_IMAGE_NAME),
            tag=os.environ.get("TAG"),
            dockerfile_dir=Path(
                os.environ.get("DOCKERFILE_DIR", DEFAULT_DOCKERFILE_DIR)
            ),
        )
        build = BuildFlags()
        runtime = RuntimeFlags(
            dry_run=False, cleanup_on_exit=not os.environ.get("NO_CLEANUP")
        )
        return cls(creds=creds, image=image, build=build, runtime=runtime)

    # ---------------------------------------------------------------------
    # High-level helpers
    # ---------------------------------------------------------------------

    def resolve(self) -> None:
        """Resolve derived/default values (username, tag, etc.)."""
        self.creds.resolve_username()
        self.image.set_default_tag(self.creds.registry)

    # ---------------------------------------------------------------------
    # Backwards-compatibility property shim
    # ---------------------------------------------------------------------
    # Registry-related
    @property
    def registry(self) -> str:  # noqa: D401
        """Return the selected container registry."""
        return self.creds.registry

    @registry.setter
    def registry(self, value: str) -> None:  # noqa: D401
        """Set the container registry."""
        self.creds.registry = value

    @property
    def docker_username(self) -> str:  # noqa: D401
        """Return the Docker Hub username used for authentication."""
        return self.creds.docker_username

    @docker_username.setter
    def docker_username(self, value: str) -> None:  # noqa: D401
        """Set the Docker Hub username."""
        self.creds.docker_username = value

    @property
    def github_username(self) -> str:  # noqa: D401
        """Return the GitHub username used for GHCR authentication."""
        return self.creds.github_username

    @github_username.setter
    def github_username(self, value: str) -> None:  # noqa: D401
        """Set the GitHub username (for GHCR pushes)."""
        self.creds.github_username = value

    @property
    def username(self) -> str:  # noqa: D401
        """Return the registry-specific username resolved at runtime."""
        return self.creds.username

    @username.setter
    def username(self, value: str) -> None:  # noqa: D401
        """Set the explicit registry username, bypassing auto-resolve."""
        self.creds.username = value

    # Image-related
    @property
    def image_name(self) -> str:  # noqa: D401
        """Return the Docker image name (without registry prefix)."""
        return self.image.image_name

    @image_name.setter
    def image_name(self, value: str) -> None:  # noqa: D401
        """Set the image name for subsequent build/tag/push steps."""
        self.image.image_name = value

    @property
    def tag(self) -> str | None:  # noqa: D401,D402
        """Return the image tag or *None* if unspecified."""
        return self.image.tag

    @tag.setter
    def tag(self, value: str | None) -> None:  # noqa: D401,D402
        """Update the image tag (``latest``/branch name/etc.)."""
        self.image.tag = value

    @property
    def dockerfile_dir(self) -> Path:  # noqa: D401
        """Return the directory containing the Dockerfile."""
        return self.image.dockerfile_dir

    @dockerfile_dir.setter
    def dockerfile_dir(self, value: Path) -> None:  # noqa: D401
        """Set the Dockerfile directory."""
        self.image.dockerfile_dir = value

    # Build flags
    @property
    def use_cache(self) -> bool:  # noqa: D401
        """Return ``True`` when Docker should leverage build cache."""
        return self.build.use_cache

    @use_cache.setter
    def use_cache(self, value: bool) -> None:  # noqa: D401
        """Enable or disable Docker build cache usage."""
        self.build.use_cache = value

    @property
    def force_rebuild(self) -> bool:  # noqa: D401
        """Return ``True`` when image should be rebuilt even if it exists."""
        return self.build.force_rebuild

    @force_rebuild.setter
    def force_rebuild(self, value: bool) -> None:  # noqa: D401
        """Toggle forced rebuild behaviour."""
        self.build.force_rebuild = value

    # Runtime flags
    @property
    def dry_run(self) -> bool:  # noqa: D401
        """Return whether commands should run in simulation mode."""
        return self.runtime.dry_run

    @dry_run.setter
    def dry_run(self, value: bool) -> None:  # noqa: D401
        """Enable or disable *dry-run* mode."""
        self.runtime.dry_run = value

    @property
    def log_level(self) -> str:  # noqa: D401
        """Return the textual log level (``normal``, ``verbose``, or ``quiet``)."""
        return self.runtime.log_level

    @log_level.setter
    def log_level(self, value: str) -> None:  # noqa: D401
        """Set the CLI log verbosity level."""
        self.runtime.log_level = value

    @property
    def cleanup_on_exit(self) -> bool:  # noqa: D401
        """Return whether locally built images are removed at program exit."""
        return self.runtime.cleanup_on_exit

    @cleanup_on_exit.setter
    def cleanup_on_exit(self, value: bool) -> None:  # noqa: D401
        """Enable or disable automatic cleanup of intermediate images."""
        self.runtime.cleanup_on_exit = value


# ---------------------------------------------------------------------------
# Env loader & validation util functions (adapted to new model)
# ---------------------------------------------------------------------------

ENV_LOCATIONS = [
    Path(".env"),
    Path.home() / ".config" / "docker-ctp" / ".env",
    Path.home() / ".docker-ctp" / ".env",
    Path("/etc/docker-ctp/.env"),
]


def load_env(config: Config) -> None:  # noqa: D401
    """Populate *os.environ* from known files and merge into *config*."""
    print(f"DEBUG: load_env before, config.dockerfile_dir={config.dockerfile_dir}")
    print(
        f"DEBUG: load_env os.environ.get('DOCKERFILE_DIR')={os.environ.get('DOCKERFILE_DIR')}"
    )
    for location in ENV_LOCATIONS:
        if location.is_file():
            logging.info("Loading configuration from %s", location)
            with location.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)
            break

    # Fold env vars into the *config* instance (using shimmed properties).
    config.docker_username = os.environ.get("DOCKER_USERNAME", config.docker_username)
    config.github_username = os.environ.get("GITHUB_USERNAME", config.github_username)
    config.image_name = os.environ.get("IMAGE_NAME", config.image_name)
    if (
        "DOCKERFILE_DIR" in os.environ
        and config.dockerfile_dir == DEFAULT_DOCKERFILE_DIR
    ):
        config.dockerfile_dir = Path(os.environ["DOCKERFILE_DIR"])
    print(f"DEBUG: load_env after, config.dockerfile_dir={config.dockerfile_dir}")
    config.registry = os.environ.get("REGISTRY", config.registry)
    if os.environ.get("NO_CLEANUP"):
        config.cleanup_on_exit = False


def validate_config(config: Config) -> None:  # noqa: D401
    """Ensure *config* is internally consistent and points to real resources."""
    print(f"DEBUG: validate_config checking {config.dockerfile_dir / 'Dockerfile'}")
    if config.registry not in {"docker", "github"}:
        raise ConfigError("Registry must be 'docker' or 'github'")
    if not config.username:
        raise ConfigError("Username is required")
    if not config.image_name:
        raise ConfigError("Image name is required")
    dockerfile = config.dockerfile_dir / "Dockerfile"
    if not dockerfile.is_file():
        print(f"DEBUG: validate_config did not find Dockerfile at {dockerfile}")
        raise ConfigError(f"Dockerfile not found at {dockerfile}")
