"""Tests for the utility functions in docker_ctp.utils."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess

import pytest
from docker_ctp.utils.build_context import validate_build_context
from docker_ctp.utils.config_generation import generate_config_files
from docker_ctp.utils.dependency_checker import check_dependencies
from docker_ctp.exceptions import DependencyError


# --- Tests for build_context.py ---


def test_validate_build_context_no_dockerignore(tmp_path: Path, caplog):
    """Verify a warning is logged if .dockerignore is missing."""
    with caplog.at_level(logging.WARNING):
        validate_build_context(tmp_path)
    assert "No .dockerignore file found" in caplog.text


def test_validate_build_context_problematic_dockerignore(tmp_path: Path, caplog):
    """Verify a warning is logged for a problematic .dockerignore."""
    dockerignore = tmp_path / ".dockerignore"
    dockerignore.write_text("**\n")
    with caplog.at_level(logging.WARNING):
        validate_build_context(tmp_path)
    assert "may exclude everything" in caplog.text


def test_validate_build_context_finds_excludables(tmp_path: Path, caplog):
    """Verify common excludable files/dirs are detected."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "test.log").touch()
    with caplog.at_level(logging.WARNING):
        validate_build_context(tmp_path)
    assert "Found files/directories that could be excluded" in caplog.text
    assert ".git" in caplog.text
    assert "node_modules" in caplog.text
    assert "*.log" in caplog.text
    assert "Add these patterns to .dockerignore" in caplog.text


def test_validate_build_context_finds_large_files(tmp_path: Path, caplog):
    """Verify large files in the build context are detected."""
    large_file = tmp_path / "large_file.bin"
    with open(large_file, "wb") as f:
        f.seek(60 * 1024 * 1024)  # 60MB
        f.write(b"\0")
    with caplog.at_level(logging.WARNING):
        validate_build_context(tmp_path)
    assert "Found large files in build context" in caplog.text
    assert "large_file.bin (60.0MB)" in caplog.text


# --- Tests for config_generation.py ---


def test_generate_config_files_creates_new(tmp_path: Path, caplog):
    """Verify config files are generated if they don't exist."""
    with patch("pathlib.Path.home", return_value=tmp_path):
        dockerignore_path = Path.cwd() / ".dockerignore"
        if dockerignore_path.exists():
            dockerignore_path.unlink()

        with caplog.at_level(logging.INFO):
            generate_config_files()

        assert "Generated:" in caplog.text
        assert ".env" in caplog.text
        assert ".dockerignore" in caplog.text
        assert (tmp_path / ".config" / "docker-ctp" / ".env").is_file()
        assert Path(".dockerignore").is_file()

        # Clean up the generated .dockerignore
        Path(".dockerignore").unlink()


def test_generate_config_files_skips_existing(tmp_path: Path, caplog):
    """Verify existing config files are not overwritten."""
    # Setup .env
    env_dir = tmp_path / ".config" / "docker-ctp"
    env_dir.mkdir(parents=True)
    (env_dir / ".env").touch()
    # Setup .dockerignore
    dockerignore_path = Path.cwd() / ".dockerignore"
    dockerignore_path.touch()

    with patch("pathlib.Path.home", return_value=tmp_path):
        with caplog.at_level(logging.INFO):
            generate_config_files()

    assert "already exists" in caplog.text
    assert "Generated:" not in caplog.text

    dockerignore_path.unlink()


def test_generate_config_files_dry_run(tmp_path: Path, caplog):
    """Verify dry-run mode does not write any files."""
    with patch("pathlib.Path.home", return_value=tmp_path):
        dockerignore_path = Path.cwd() / ".dockerignore"
        if dockerignore_path.exists():
            dockerignore_path.unlink()

        with caplog.at_level(logging.INFO):
            generate_config_files(dry_run=True)

        assert "DRY-RUN: Would write" in caplog.text
        assert not (tmp_path / ".config" / "docker-ctp" / ".env").exists()
        assert not dockerignore_path.exists()


# --- Tests for dependency_checker.py ---


@patch("shutil.which", return_value="/usr/bin/docker")
@patch("subprocess.run", return_value=MagicMock(returncode=0))
def test_check_dependencies_success(mock_run, mock_which, caplog):
    """Test successful dependency check."""
    with caplog.at_level(logging.INFO):
        check_dependencies(dry_run=False)
    assert "Docker executable found" in caplog.text
    assert "Docker daemon is running" in caplog.text
    mock_which.assert_called_with("docker")
    mock_run.assert_called_with(
        ["docker", "info"],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


@patch("shutil.which", return_value=None)
def test_check_dependencies_no_docker(_mock_which):
    """Test when docker executable is not found."""
    with pytest.raises(DependencyError, match="Docker is not installed"):
        check_dependencies(dry_run=False)


@patch("shutil.which", return_value="/usr/bin/docker")
@patch(
    "subprocess.run",
    side_effect=subprocess.CalledProcessError(1, "docker info"),
)
def test_check_dependencies_daemon_not_running(_mock_run, _mock_which):
    """Test when docker daemon is not running."""
    with pytest.raises(DependencyError, match="Docker daemon is not running"):
        check_dependencies(dry_run=False)


def test_check_dependencies_dry_run(caplog):
    """Test that daemon check is skipped in dry-run mode."""
    with patch("shutil.which", return_value="/usr/bin/docker"):
        with patch("subprocess.run") as mock_run:
            with caplog.at_level(logging.INFO):
                check_dependencies(dry_run=True)
            assert "Skipping Docker daemon check" in caplog.text
            mock_run.assert_not_called()
