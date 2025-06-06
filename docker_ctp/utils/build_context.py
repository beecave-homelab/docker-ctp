"""Build context validation utilities."""

from __future__ import annotations

import logging
from pathlib import Path


def validate_build_context(path: Path) -> None:
    """Check for .dockerignore and warn about large files."""
    dockerignore = path / ".dockerignore"
    if not dockerignore.is_file():
        logging.warning(".dockerignore not found in %s", path)
    else:
        with dockerignore.open("r", encoding="utf-8") as handle:
            for num, line in enumerate(handle, start=1):
                if "**" == line.strip():
                    logging.warning(".dockerignore line %s ignores everything", num)

    for file in path.rglob("*"):
        if file.is_file() and file.stat().st_size > 50 * 1024 * 1024:
            logging.warning("Large file in build context: %s", file)
