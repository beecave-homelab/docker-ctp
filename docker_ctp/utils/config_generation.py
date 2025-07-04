"""Configuration file generation utilities."""

from __future__ import annotations

from pathlib import Path

from docker_ctp.utils.logging_utils import get_message_handler

# Centralised Rich-based message handler
messages = get_message_handler()

__all__: list[str] = [
    "generate_config_files",
]

ENV_TEMPLATE = """# Docker CTP Configuration File
# Auto-generated by docker-ctp --generate-config

# Docker Hub username used for authentication
DOCKER_USERNAME="your-dockerhub-username"

# GitHub username (personal or organization account) for repository access
GITHUB_USERNAME="your-github-username"

# Directory where the Dockerfile is located (default is current directory)
DOCKERFILE_DIR="."

# Registry to which the Docker image will be pushed (either "docker" or "github")
REGISTRY="docker"

# Default tag for DockerHub images
DEFAULT_DOCKERHUB_TAG="latest"

# Default tag for GitHub images
DEFAULT_GITHUB_TAG="main"

# Authentication tokens (RECOMMENDED for security and automation)
# Docker Hub Personal Access Token (preferred over DOCKER_PASSWORD)
# DOCKER_TOKEN="your_docker_hub_pat_here"

# Alternative: Docker Hub password (less secure, use DOCKER_TOKEN instead)
# DOCKER_PASSWORD="your_docker_hub_password_here"

# GitHub Personal Access Token for GitHub Container Registry
# GITHUB_TOKEN="your_github_pat_here"

# Alternative GitHub Container Registry token name
# GHCR_TOKEN="your_github_pat_here"

# Build and optimization settings
# USE_CACHE=true
# FORCE_REBUILD=false
# LOG_LEVEL="normal"  # Options: quiet, normal, verbose
# CLEANUP_ON_EXIT=true
"""

DOCKERIGNORE_TEMPLATE = """# Docker CTP - Dockerignore Template
# Auto-generated by docker-ctp --generate-config

# Version control
.git
.gitignore
.gitattributes

# Development files
.vscode
.idea
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
/tmp

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Documentation (adjust as needed)
README.md
*.md
docs/

# Testing
test/
tests/
coverage/
.nyc_output

# Build artifacts (adjust as needed)
# build/
# dist/

# Environment files (keep sensitive data out of images)
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
"""


def generate_config_files(dry_run: bool = False) -> None:  # noqa: D401
    """Generate default .env and .dockerignore files."""
    messages.info("Generating default configuration files...")

    # --- Generate .env file in user's config directory ---
    generated_files = []
    env_path = Path.home() / ".config" / "docker-ctp" / ".env"

    if env_path.exists():
        messages.warning("Configuration file already exists: %s", env_path)
        messages.info("Skipping to avoid overwriting existing configuration.")
    else:
        messages.info("Generating configuration file: %s", env_path)
        if dry_run:
            messages.info("DRY-RUN: Would create directory %s", env_path.parent)
            messages.info("DRY-RUN: Would write .env template to %s", env_path)
        else:
            try:
                env_path.parent.mkdir(parents=True, exist_ok=True)
                env_path.write_text(ENV_TEMPLATE, encoding="utf-8")
                messages.info("✓ Generated: %s", env_path)
                generated_files.append(str(env_path))
            except OSError as e:
                messages.error("Failed to generate %s: %s", env_path, e)

    # --- Generate .dockerignore in current directory ---
    dockerignore_path = Path(".dockerignore")
    if dockerignore_path.exists():
        messages.info(".dockerignore already exists - skipping template generation.")
    else:
        messages.info("Generating .dockerignore template: %s", dockerignore_path)
        if dry_run:
            messages.info(
                "DRY-RUN: Would write .dockerignore template to %s", dockerignore_path
            )
        else:
            try:
                dockerignore_path.write_text(DOCKERIGNORE_TEMPLATE, encoding="utf-8")
                messages.info("✓ Generated: %s", dockerignore_path)
                generated_files.append(str(dockerignore_path))
            except OSError as e:
                messages.error("Failed to generate %s: %s", dockerignore_path, e)

    # --- Provide summary and next steps ---
    if generated_files:
        messages.info("Configuration generation completed!")
        messages.info("")
        messages.info("📋 Generated files:")
        for file in generated_files:
            messages.info("  - %s", file)
        messages.info("")
        messages.info("🔧 Next steps:")
        messages.info("  1. Edit the .env file with your actual values: %s", env_path)
        messages.info(
            "  2. Set auth tokens (DOCKER_TOKEN/GITHUB_TOKEN) in the .env file."
        )
        messages.info(
            "  3. Review and customize .dockerignore in the current directory."
        )
        messages.info("  4. Run 'docker-ctp --dry-run' to test your configuration.")
        messages.info("")
        messages.warning(
            "⚠️  Remember to add .env files to your global .gitignore to protect "
            "sensitive tokens!"
        )
    elif not dry_run:
        messages.info("No new configuration files were generated.")
