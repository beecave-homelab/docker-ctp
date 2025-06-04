# README.md

# docker-ctp

This script builds, tags, and pushes a Docker image to Docker Hub or GitHub Container Registry, depending on the selected registry.

## Versions
**Current version**: 0.4.0

## Table of Contents
- [Versions](#versions)
- [Features](#features)
- [Badges](#badges)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Build Optimizations](#build-optimizations)
- [License](#license)
- [Contributing](#contributing)

## Badges
![Shell Script](https://img.shields.io/badge/language-shell-blue)
![Version](https://img.shields.io/badge/version-0.4.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Dual Registry Support**: Push images to Docker Hub or GitHub Container Registry.
- **Flexible Configuration**: 
    - Command-line arguments.
    - Environment variables.
    - `.env` files (searches multiple standard locations, e.g., `./.env`, `~/.config/docker-ctp/.env`).
    - Clear priority: CLI > ENV > `.env` > Defaults.
- **Secure Token Handling**: Prioritizes environment variables (`DOCKER_TOKEN`, `GITHUB_TOKEN`) for authentication, with interactive fallback if run in a TTY.
- **Comprehensive Input Validation**: Sanitizes and validates usernames, image names, tags, paths, and registry choices.
- **Dry Run Mode**: Use `--dry-run` to simulate all operations without actual execution.
- **Adjustable Logging**: 
    - `--verbose` for detailed output.
    - `--quiet` to suppress informational logs (errors still shown).
    - Normal mode for balanced output.
- **Dependency Checking**: Verifies essential tools (Docker, realpath, etc.) and Docker daemon status.
- **Smart Image Rebuild**: Avoids rebuilding if an image with the target tag already exists. Use `--force-rebuild` to override.
- **Build Context Validation**: 
    - Checks for `.dockerignore` file and basic syntax.
    - Warns about common unignored files/directories (e.g., `.git`, `node_modules`).
    - Alerts for potentially very large files in the build context.
- **Automatic Cleanup**: Removes intermediate Docker images created during the process (build and tagged images before push). Use `--no-cleanup` to disable.
- **Configuration File Generation**: Use `--generate-config` to create a template `.env` file and a comprehensive `.dockerignore` file.
- **Helpful Output**: Progress indicators for long operations, clear success/error/warning messages, and ASCII art for flair!

## Installation

1.  **Get the script**:
    *   Clone the repository (if you want the full project structure):
        ```bash
        git clone <your-repository-url> # Replace with actual URL if public
        cd docker-ctp
        ```
    *   Or, download/copy the `docker-ctp.sh` script to your system.

2.  **Make the script executable**:
    ```bash
    chmod +x docker-ctp.sh
    ```

3.  **Generate initial configuration files (recommended)**:
    Run the script with the `--generate-config` flag. This will create a `.env` template in the current directory and a `.dockerignore` file.
    ```bash
    ./docker-ctp.sh --generate-config
    ```

4.  **Edit your `.env` file**:
    Open the generated `.env` file (e.g., the one in your current project directory) and fill in your details, especially:
    *   `DOCKER_USERNAME` (your Docker Hub username)
    *   `GITHUB_USERNAME` (your GitHub username or organization)
    *   `DOCKER_TOKEN` (your Docker Hub Personal Access Token - PAT)
    *   `GITHUB_TOKEN` (your GitHub Personal Access Token - PAT with `write:packages` scope)
    *   Optionally, `REGISTRY`, `DOCKERFILE_DIR`, `DEFAULT_DOCKERHUB_TAG`, `DEFAULT_GITHUB_TAG` if you want to set project-level defaults different from the script's internal defaults.

    **Important**: Add your `.env` file to your project's `.gitignore` to avoid committing sensitive tokens!

## Usage

To use the script, run it with the following command:
```bash
./docker-ctp.sh [OPTIONS]
```

**Options**:

```
  -u, --username         Docker Hub or GitHub username (default: Docker Hub: your_user, GitHub: your_user)
  -i, --image-name       Docker image name (default: current_directory_name)
  -t, --image-tag        Docker image tag (default: 'latest' for Docker, 'main' for GitHub)
  -d, --dockerfile-dir   Path to Dockerfile folder (default: .)
  -g, --registry         Target registry (default: docker; 'docker' for Docker Hub, 'github' for GitHub)
  --no-cache             Disable Docker cache and force a clean build (default: use cache)
  --force-rebuild        Force rebuild even if image already exists (default: skip if exists)
  --dry-run              Simulate operations without executing them (default: false)
  --verbose              Enable verbose logging (default: normal)
  --quiet                Suppress non-error output (default: false)
  --no-cleanup           Disable cleanup of intermediate images (default: enable cleanup)
  --generate-config      Generate default configuration files (.env and .dockerignore)
  --version              Show version information
  -h, --help             Display this help message
```
*Note: Default values for username, image name, and registry in the help text above are illustrative and will reflect your local configuration or script defaults when you run `--help`.*

**Examples**:

```bash
# Generate default configuration files (.env, .dockerignore)
./docker-ctp.sh --generate-config

# Perform a dry run for Docker Hub, assuming .env is configured
./docker-ctp.sh --dry-run --registry docker

# Build and push to GitHub Container Registry with verbose logging
# (assumes GITHUB_USERNAME and GITHUB_TOKEN are in .env or ENV)
./docker-ctp.sh --verbose --registry github --image-name myapp --image-tag v1.0.1

# Force a clean rebuild (no cache) and push to Docker Hub with a specific Dockerfile location
./docker-ctp.sh --no-cache --force-rebuild --registry docker -u mydockeruser -i myimage -t latest -d ./build/context

# Push to GitHub in quiet mode, disable cleanup
./docker-ctp.sh --quiet --no-cleanup --registry github -u mygituser -i anotherapp -t main
```

## Configuration

The script offers a flexible configuration system, loading settings in the following order of precedence (highest to lowest):

1.  **Command-line arguments**: Options like `-u`, `-i`, `-g`, etc., always take top priority.
2.  **Environment variables**: You can set script variables (e.g., `DOCKER_USERNAME`, `REGISTRY`, `TAG`, `LOG_LEVEL`) in your shell environment. These will override settings from `.env` files and script defaults.
3.  **`.env` file**: The script automatically searches for and loads an `.env` file from the following locations, using the first one it finds:
    1.  `./.env` (Current project directory - highest priority for `.env` files)
    2.  `$HOME/.config/docker-ctp/.env` (User-level global config)
    3.  `$HOME/.docker-ctp/.env` (Alternative user-level global config)
    4.  `/etc/docker-ctp/.env` (System-wide config - lowest priority for `.env` files)
4.  **Script defaults**: If a setting is not found via CLI, ENV, or `.env`, the script uses its internal default values (e.g., `IMAGE_NAME` defaults to the current directory name, `REGISTRY` defaults to `docker`).

**Key `.env` Variables (and corresponding Environment Variables)**:

Refer to the `.env.example` file (or generate one using `--generate-config`) for a full list of supported variables. Key ones include:

*   `DOCKER_USERNAME`: Your Docker Hub username. (Defaults to system `$USER` if not set anywhere).
*   `GITHUB_USERNAME`: Your GitHub username or organization name. (Defaults to system `$USER` if not set anywhere).
*   `IMAGE_NAME`: Default image name if not provided by `-i` CLI argument. (Script default: current directory name).
*   `DOCKERFILE_DIR`: Path to the directory containing your `Dockerfile`. (Script default: `.`)
*   `REGISTRY`: Target registry: `docker` or `github`. (Script default: `docker`)
*   `DEFAULT_DOCKERHUB_TAG`: Default tag to use if `REGISTRY` is `docker` and `-t` is not provided. (Script default: `latest`)
*   `DEFAULT_GITHUB_TAG`: Default tag to use if `REGISTRY` is `github` and `-t` is not provided. (Script default: `main`)
*   `DOCKER_TOKEN`: Your Docker Hub Personal Access Token (PAT). **Recommended for authentication.**
*   `DOCKER_PASSWORD`: Alternative Docker Hub password (less secure, `DOCKER_TOKEN` preferred).
*   `GITHUB_TOKEN` / `GHCR_TOKEN`: Your GitHub PAT with `write:packages` scope for GitHub Container Registry. **Recommended for authentication.**

**Other Script Behaviors via `.env` / Environment Variables**:

These boolean flags or settings can also be controlled via environment variables (e.g., `export LOG_LEVEL="verbose"` or by setting them in your `.env` file like `LOG_LEVEL="verbose"`). CLI flags still take precedence.

*   `USE_CACHE=true|false` (Corresponds to `--no-cache` flag; `false` means no cache)
*   `FORCE_REBUILD=true|false` (Corresponds to `--force-rebuild` flag)
*   `DRY_RUN=true|false` (Corresponds to `--dry-run` flag)
*   `LOG_LEVEL="quiet"|"normal"|"verbose"` (Corresponds to `--quiet` and `--verbose` flags)
*   `CLEANUP_ON_EXIT=true|false` (Corresponds to `--no-cleanup` flag; `false` means no cleanup)

## Build Optimizations

The script includes features to help optimize your Docker build process and reduce unnecessary rebuilds.

### Smart Image Rebuild

*   By default, before starting a build, `docker-ctp.sh` checks if a Docker image with the exact target name and tag already exists locally.
*   If a matching image is found, the build step is skipped, and the script proceeds directly to tagging (if necessary for the target registry) and pushing. This can save significant time during development and in CI/CD pipelines when no code changes have occurred.
*   To override this behavior and force a rebuild even if the image exists, use the `--force-rebuild` command-line flag.

### Build Context Validation

To help prevent excessively large or slow Docker builds due to an unoptimized build context, the script performs several checks on your Dockerfile directory:

*   **`.dockerignore` File**: 
    *   It checks for the presence of a `.dockerignore` file. If missing, a warning is issued, as this is crucial for excluding unnecessary files from the build context sent to the Docker daemon.
    *   It performs a basic syntax check (e.g., warns if the `.dockerignore` contains `**` on its own line, which would ignore everything).
*   **Common Excludes**: The script checks for common files and directories that are often unintentionally included in the build context (e.g., `.git` directory, `node_modules`, `*.log` files, `README.md`). If found and not mentioned in `.dockerignore`, it will suggest adding them.
*   **Large Files**: It scans for very large files (e.g., >50MB) directly within the build context (first two levels) and warns about them, as these can significantly slow down builds or inflate image size.

These validation messages are typically shown when `--verbose` logging is enabled, or as warnings if issues are detected.

## License
This project is licensed under the MIT license. See [LICENSE](LICENSE) for more information.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.