"""Unit tests for the new modular Config implementation."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

from docker_ctp.config import (
    Config,
    DEFAULT_DOCKERHUB_TAG,
    DEFAULT_GITHUB_TAG,
    validate_config,
)
from docker_ctp.exceptions import ConfigError


@pytest.fixture()
def tmp_dockerfile(tmp_path: Path):
    """Create a minimal Dockerfile in *tmp_path* and return the directory."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM scratch\n")
    return tmp_path


def test_username_resolution_docker(tmp_dockerfile: Path):
    cfg = Config()
    cfg.dockerfile_dir = tmp_dockerfile
    cfg.resolve()
    # For the default registry (docker), username should fallback to docker_username
    assert cfg.username == cfg.docker_username


def test_username_resolution_github(tmp_dockerfile: Path):
    cfg = Config()
    cfg.registry = "github"
    cfg.dockerfile_dir = tmp_dockerfile
    cfg.resolve()
    assert cfg.username == cfg.github_username


def test_default_tags(tmp_dockerfile: Path):
    # Docker registry ⇒ latest
    cfg_docker = Config()
    cfg_docker.dockerfile_dir = tmp_dockerfile
    cfg_docker.resolve()
    assert cfg_docker.tag == DEFAULT_DOCKERHUB_TAG

    # GitHub registry ⇒ main
    cfg_gh = Config()
    cfg_gh.registry = "github"
    cfg_gh.dockerfile_dir = tmp_dockerfile
    cfg_gh.resolve()
    assert cfg_gh.tag == DEFAULT_GITHUB_TAG


def test_validate_config_success(tmp_dockerfile: Path):
    cfg = Config()
    cfg.dockerfile_dir = tmp_dockerfile
    cfg.resolve()
    # Should not raise
    validate_config(cfg)


def test_validate_config_missing_dockerfile(tmp_path: Path):
    cfg = Config()
    cfg.dockerfile_dir = tmp_path  # directory without Dockerfile
    cfg.resolve()
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_from_cli_mapping(tmp_dockerfile: Path):
    args = Namespace(
        registry="docker",
        username="cliuser",
        image_name="myimage",
        tag="1.0.0",
        dockerfile_dir=str(tmp_dockerfile),
        no_cache=True,
        force_rebuild=True,
        dry_run=True,
        verbose=True,
        quiet=False,
        no_cleanup=True,
    )

    cfg = Config.from_cli(args)

    assert cfg.registry == "docker"
    assert cfg.username == "cliuser"
    assert cfg.image_name == "myimage"
    assert cfg.tag == "1.0.0"
    assert cfg.dockerfile_dir == tmp_dockerfile
    assert cfg.use_cache is False  # because --no-cache
    assert cfg.force_rebuild is True
    assert cfg.dry_run is True
    assert cfg.cleanup_on_exit is False
    # Resolve should be idempotent even after defaults are set
    cfg.resolve()
    validate_config(cfg)


def test_validate_config_invalid_registry(tmp_dockerfile: Path):
    cfg = Config()
    cfg.dockerfile_dir = tmp_dockerfile
    cfg.registry = "invalid"
    cfg.resolve()
    with pytest.raises(ConfigError) as excinfo:
        validate_config(cfg)
    assert "Registry must be" in str(excinfo.value)
