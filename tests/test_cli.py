"""Tests for the Click-based CLI."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

import pytest

from docker_ctp.cli import cli


@pytest.fixture(autouse=True)
def _set_env_token(monkeypatch):
    """Ensure a dummy Docker token is available so login() doesn't crash."""
    monkeypatch.setenv("DOCKER_TOKEN", "dummy")
    monkeypatch.setenv("GITHUB_TOKEN", "dummy")
    monkeypatch.setenv("REGISTRY", "docker")


@pytest.fixture()
def minimal_dockerfile(tmp_path: Path) -> Path:
    """Return a directory containing a minimal Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM scratch\n")
    return tmp_path


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "docker-ctp" in result.output


def test_cli_dry_run_success(minimal_dockerfile: Path):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--dry-run",
            "--username",
            "tester",
            "--image-name",
            "myimage",
            "--image-tag",
            "1.0.0",
            "--dockerfile-dir",
            str(minimal_dockerfile),
        ],
    )
    assert result.exit_code == 0
    # Should go through pipeline and log completion message
    assert "Completed" in result.output


def test_cli_invalid_username(minimal_dockerfile: Path):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--dry-run",
            "--username",
            "!!!invalid!!!",
            "--image-name",
            "myimage",
            "--image-tag",
            "1.0.0",
            "--dockerfile-dir",
            str(minimal_dockerfile),
        ],
    )
    assert result.exit_code == 1
    assert "Invalid username" in result.output
    assert "Error:" in result.output


def test_cli_missing_dockerfile(tmp_path: Path):
    print(f"DEBUG: test_cli_missing_dockerfile tmp_path={tmp_path}")
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--dry-run",
            "--username",
            "tester",
            "--image-name",
            "myimage",
            "--image-tag",
            "1.0.0",
            "--dockerfile-dir",
            str(tmp_path),  # Directory without Dockerfile
        ],
    )
    print(f"DEBUG: output={result.output!r}")
    print(f"DEBUG: exception={result.exception!r}")
    assert result.exit_code == 1
    assert "Dockerfile not found" in result.output
    assert "Error:" in result.output
