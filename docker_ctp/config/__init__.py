"""Configuration management for docker-ctp."""

from __future__ import annotations

import logging
from dataclasses import MISSING, dataclass, field
from dataclasses import fields as dataclass_fields
from pathlib import Path
from types import SimpleNamespace
from typing import TypeAlias

from docker_ctp.utils.env import get_env

DEFAULT_DOCKER_USERNAME = get_env("USER", "")
DEFAULT_GITHUB_USERNAME = get_env("USER", "")
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
            image_name=args.image_name or Path(args.dockerfile_dir).resolve().name,
            tag=args.tag,
            dockerfile_dir=Path(args.dockerfile_dir),
        )
        build = BuildFlags(
            use_cache=not args.no_cache, force_rebuild=args.force_rebuild
        )
        runtime = RuntimeFlags(
            dry_run=args.dry_run,
            log_level=(
                "verbose" if args.verbose else "quiet" if args.quiet else "normal"
            ),
            cleanup_on_exit=not args.no_cleanup,
        )
        return cls(creds=creds, image=image, build=build, runtime=runtime)

    @classmethod
    def from_env(cls) -> "Config":
        """Create a Config instance solely from environment variables."""
        creds = RegistryCredentials(
            registry=get_env("REGISTRY", DEFAULT_REGISTRY),
            docker_username=get_env("DOCKER_USERNAME", DEFAULT_DOCKER_USERNAME),
            github_username=get_env("GITHUB_USERNAME", DEFAULT_GITHUB_USERNAME),
            username=get_env("USERNAME", ""),
        )
        image = ImageInfo(
            image_name=get_env("IMAGE_NAME", DEFAULT_IMAGE_NAME),
            tag=get_env("TAG"),
            dockerfile_dir=Path(get_env("DOCKERFILE_DIR", DEFAULT_DOCKERFILE_DIR)),
        )
        build = BuildFlags()
        runtime = RuntimeFlags(dry_run=False, cleanup_on_exit=not get_env("NO_CLEANUP"))
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

ConfigSection: TypeAlias = RegistryCredentials | ImageInfo | BuildFlags | RuntimeFlags

ENV_LOCATIONS = [
    Path(".env"),
    Path.home() / ".config" / "docker-ctp" / ".env",
    Path.home() / ".docker-ctp" / ".env",
    Path("/etc/docker-ctp/.env"),
]


def _get_field_default(dc_instance: ConfigSection, field_name: str):
    """Return the default value for *field_name* on a dataclass *instance*."""
    for f in dataclass_fields(dc_instance):
        if f.name == field_name:
            if f.default is not MISSING:
                return f.default
            if f.default_factory is not MISSING:  # type: ignore[attr-defined]
                return f.default_factory()  # type: ignore[misc]
    return None


def load_env(config: Config) -> None:  # noqa: D401
    """Populate *os.environ* from known files and merge into *config*."""
    search_paths: list[Path] = []
    # 1. Conditionally add ./.env
    if Path.cwd().name == "docker-ctp":
        search_paths.append(Path.cwd() / ".env")
    # 2. Conditionally add ~/.config/docker-ctp/.env
    search_paths.append(Path.home() / ".config" / "docker-ctp" / ".env")
    # 3. Conditionally add ~/.docker-ctp/.env
    search_paths.append(Path.home() / ".docker-ctp" / ".env")
    # 4. Conditionally add /etc/docker-ctp/.env
    search_paths.append(Path("/etc/docker-ctp/.env"))

    for env_path in search_paths:
        if env_path.is_file():
            logging.info("Loading configuration from %s", env_path)
            with env_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip().lower()
                    value = value.strip().strip("'\"")

                    # Find the correct sub-config and update it
                    for sub_config in (
                        config.creds,
                        config.image,
                        config.build,
                        config.runtime,
                    ):
                        if hasattr(sub_config, key):
                            current = getattr(sub_config, key)
                            default_val = _get_field_default(sub_config, key)
                            # Skip overriding when the *current* value differs from the
                            # dataclass default – this usually means the value came from
                            # CLI args and should win over the .env.
                            if current != default_val:
                                continue
                            # Handle type conversions
                            if isinstance(current, bool):
                                setattr(sub_config, key, value.lower() == "true")
                            elif isinstance(current, Path):
                                setattr(sub_config, key, Path(value))
                            else:
                                setattr(sub_config, key, value)
                            break  # Move to next line in .env file

            config.resolve()  # Re-resolve dynamic values after loading .env
            return

    logging.info("No .env file found in search paths. Using defaults/CLI args.")
