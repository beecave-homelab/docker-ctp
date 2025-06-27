"""Dependency checking utilities."""

from __future__ import annotations

import shutil
import subprocess
from ..exceptions import DependencyError

REQUIRED_TOOLS = ["docker", "realpath", "basename", "grep"]


def check_dependencies(dry_run: bool) -> None:
    """Verify that required system dependencies are available."""
    missing = [tool for tool in REQUIRED_TOOLS if shutil.which(tool) is None]
    if missing:
        raise DependencyError(f"Missing required dependencies: {', '.join(missing)}")

    if dry_run:
        return

    try:
        subprocess.run(["docker", "info"], check=True, capture_output=True)
    except Exception as exc:  # pragma: no cover - docker may not be available
        raise DependencyError("Docker daemon is not running") from exc
