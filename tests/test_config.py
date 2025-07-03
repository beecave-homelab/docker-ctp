"""Unit tests for the new modular Config implementation."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from docker_ctp.config import (
    Config,
    DEFAULT_DOCKERHUB_TAG,
    DEFAULT_GITHUB_TAG,
    load_env,
)


@pytest.fixture()
def _tmp_dockerfile(tmp_path: Path):
    """Create a minimal Dockerfile in *tmp_path* and return the directory."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM scratch\n")
    return tmp_path


def test_username_resolution_docker(_tmp_dockerfile: Path):
    """Test that username resolves to the Docker default."""
    cfg = Config()
    cfg.dockerfile_dir = _tmp_dockerfile
    cfg.resolve()
    # For the default registry (docker), username should fallback to docker_username
    assert cfg.username == cfg.docker_username


def test_username_resolution_github(_tmp_dockerfile: Path):
    """Test that username resolves to the GitHub default."""
    cfg = Config()
    cfg.registry = "github"
    cfg.dockerfile_dir = _tmp_dockerfile
    cfg.resolve()
    assert cfg.username == cfg.github_username


def test_default_tags(_tmp_dockerfile: Path):
    """Verify that default tags are correctly applied."""
    # Docker registry ⇒ latest
    cfg_docker = Config()
    cfg_docker.dockerfile_dir = _tmp_dockerfile
    cfg_docker.resolve()
    assert cfg_docker.tag == DEFAULT_DOCKERHUB_TAG

    # GitHub registry ⇒ main
    cfg_gh = Config()
    cfg_gh.registry = "github"
    cfg_gh.dockerfile_dir = _tmp_dockerfile
    cfg_gh.resolve()
    assert cfg_gh.tag == DEFAULT_GITHUB_TAG


def test_from_cli_mapping(_tmp_dockerfile: Path):
    """Verify that CLI arguments are correctly mapped to Config fields."""
    args = Namespace(
        registry="docker",
        username="cliuser",
        image_name="myimage",
        tag="1.0.0",
        dockerfile_dir=str(_tmp_dockerfile),
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
    assert cfg.dockerfile_dir == _tmp_dockerfile
    assert cfg.use_cache is False  # because --no-cache
    assert cfg.force_rebuild is True
    assert cfg.dry_run is True
    assert cfg.cleanup_on_exit is False
    # Resolve should be idempotent even after defaults are set
    cfg.resolve()


# --- Tests for .env loading ---


def test_load_env_loads_from_project_root(tmp_path: Path):
    """Verify .env is loaded from project root if cwd is 'docker-ctp'."""
    project_dir = tmp_path / "docker-ctp"
    project_dir.mkdir()
    (project_dir / ".env").write_text("IMAGE_NAME=from-project-env")

    cfg = Config()
    with patch("pathlib.Path.cwd", return_value=project_dir):
        load_env(cfg)

    assert cfg.image_name == "from-project-env"


def test_load_env_skips_project_root_if_not_named_docker_ctp(tmp_path: Path):
    """Verify .env is NOT loaded from project root if cwd is not 'docker-ctp'."""
    project_dir = tmp_path / "not-docker-ctp"
    project_dir.mkdir()
    (project_dir / ".env").write_text("IMAGE_NAME=should-not-be-loaded")

    # Set up a home-directory .env to prove it falls back
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    config_dir = home_dir / ".config" / "docker-ctp"
    config_dir.mkdir(parents=True)
    (config_dir / ".env").write_text("IMAGE_NAME=from-home-config")

    cfg = Config()
    with patch("pathlib.Path.cwd", return_value=project_dir):
        with patch("pathlib.Path.home", return_value=home_dir):
            load_env(cfg)

    assert cfg.image_name == "from-home-config"


def test_load_env_priority_order(tmp_path: Path):
    """Verify the search path priority is correctly followed."""
    # 1. Highest priority: project root ./docker-ctp/.env
    project_dir = tmp_path / "docker-ctp"
    project_dir.mkdir()
    (project_dir / ".env").write_text("REGISTRY=from-project-root")

    # 2. Next priority: ~/.config/docker-ctp/.env
    home_dir = tmp_path / "home"
    config_dir = home_dir / ".config" / "docker-ctp"
    config_dir.mkdir(parents=True)
    (config_dir / ".env").write_text("REGISTRY=from-home-config")

    # 3. Lower priority: ~/.docker-ctp/.env
    (home_dir / ".docker-ctp").mkdir()
    (home_dir / ".docker-ctp" / ".env").write_text("REGISTRY=from-home-root")

    cfg = Config()
    # When cwd is docker-ctp, it should load from there
    with patch("pathlib.Path.cwd", return_value=project_dir):
        with patch("pathlib.Path.home", return_value=home_dir):
            load_env(cfg)
    assert cfg.registry == "from-project-root"

    # When cwd is something else, it should load from home/.config
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    cfg_other = Config()
    with patch("pathlib.Path.cwd", return_value=other_dir):
        with patch("pathlib.Path.home", return_value=home_dir):
            load_env(cfg_other)
    assert cfg_other.registry == "from-home-config"
