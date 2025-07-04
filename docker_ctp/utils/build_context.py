"""Build context validation utilities."""

from __future__ import annotations

from pathlib import Path

from docker_ctp.utils.logging_utils import get_message_handler

# Centralised Rich-based message handler
messages = get_message_handler()

__all__: list[str] = [
    "validate_build_context",
]

# Files/directories to check for if they are not in .dockerignore
COMMON_EXCLUDES = [
    ".git",
    "node_modules",
    "*.log",
    "*.tmp",
    ".DS_Store",
    "Thumbs.db",
    "*.swp",
    "*.swo",
    ".vscode",
    ".idea",
    "coverage",
    "test",
    "tests",
    "*.md",
    "README*",
]

LARGE_FILE_THRESHOLD_BYTES = 50 * 1024 * 1024  # 50MB


def validate_build_context(dockerfile_dir: Path) -> None:  # noqa: D401
    """Check for .dockerignore, large files, and other common issues."""
    messages.info("Validating build context in %s...", dockerfile_dir)
    warnings = 0
    suggestions = []

    # 1. Validate .dockerignore file
    dockerignore_path = dockerfile_dir / ".dockerignore"
    if not dockerignore_path.is_file():
        messages.warning("No .dockerignore file found in build context.")
        suggestions.append(
            "Create a .dockerignore file to exclude unnecessary files and "
            "optimize build context."
        )
        warnings += 1
    else:
        messages.info("✓ .dockerignore file found.")
        try:
            with dockerignore_path.open("r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if line.strip() == "**":
                        messages.warning(
                            ".dockerignore line %s ('**') may exclude everything.", i
                        )
                        warnings += 1
        except OSError as e:
            messages.warning("Could not read .dockerignore file: %s", e)
            warnings += 1

    # 2. Check for common excludable files/directories
    found_excludables = []
    for pattern in COMMON_EXCLUDES:
        # Simple check for directories
        if not pattern.startswith("*") and (dockerfile_dir / pattern).is_dir():
            found_excludables.append(pattern)
        # Check for file patterns
        elif "*" in pattern:
            if next(dockerfile_dir.glob(pattern), None):
                found_excludables.append(pattern)

    if found_excludables:
        messages.warning("Found files/directories that could be excluded:")
        for excludable in found_excludables:
            messages.warning("  - %s", excludable)
        suggestions.append(
            f"Add these patterns to .dockerignore: {', '.join(found_excludables)}"
        )
        # Provide immediate actionable suggestion at WARNING level for better visibility/testability
        messages.warning(
            "Add these patterns to .dockerignore: %s", ", ".join(found_excludables)
        )
        warnings += 1

    # 3. Check for large files
    large_files = []
    try:
        for file in dockerfile_dir.rglob("*"):
            if not file.is_file():
                continue
            try:
                if file.stat().st_size > LARGE_FILE_THRESHOLD_BYTES:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    large_files.append(f"{file.name} ({size_mb:.1f}MB)")
            except FileNotFoundError:
                # File might be a broken symlink, skip it
                continue
    except OSError as e:
        messages.warning("Could not scan for large files: %s", e)

    if large_files:
        messages.warning("Found large files in build context:")
        for large_file in large_files:
            messages.warning("  - %s", large_file)
        suggestions.append(
            "Consider excluding large files or using multi-stage builds to "
            "reduce image size."
        )
        warnings += 1

    # 4. Final summary
    if warnings == 0:
        messages.info("✓ Build context validation passed with no issues.")
    else:
        messages.warning(
            "Build context validation completed with %d warnings.", warnings
        )
        if suggestions:
            messages.info("Optimization suggestions:")
            for suggestion in suggestions:
                messages.info("  - %s", suggestion)
