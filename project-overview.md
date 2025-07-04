---
repo: https://github.com/beecave-homelab/docker-ctp.git
commit: f948c2fbf978b7d88e4e6fdb32e6746684526b03
generated: 2025-07-03T22:42:08Z
---
<!-- SECTIONS:API,CLI,WEBUI,CI,DOCKER,TESTS -->

# Project Overview | docker-ctp

A Python-based tool and shell script for building, tagging, and pushing Docker images to Docker Hub or GitHub Container Registry. Designed for developers and CI/CD workflows needing reproducible container builds.

[![Language](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.4.0-brightgreen)](#version-summary)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](Dockerfile)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Pydocstyle](https://img.shields.io/badge/docs%20style-pydocstyle-blue.svg)](https://github.com/PyCQA/pydocstyle)
[![Pytest](https://img.shields.io/badge/tests-pytest-green)](https://docs.pytest.org/en/stable/)

> **Status:** Package now fully matches the original `docker-ctp.sh` feature set (_July 2025_).

## Table of Contents

- [Quickstart for Developers](#quickstart-for-developers)
- [Version Summary](#version-summary)
- [Project Features](#project-features)
- [Project Structure](#project-structure)
- [Architecture Highlights](#architecture-highlights)
- [API](#api)
- [CLI](#cli)
- [WebUI](#webui)
- [Code Quality](#code-quality)
- [Docker](#docker)
- [Tests](#tests)
- [Recent Improvements](#recent-improvements)

## Quickstart for Developers

```bash
git clone https://github.com/beecave-homelab/docker-ctp.git
pipx install "git+https://github.com/beecave-homelab/docker-ctp.git"
# or for development:
pdm install
```

## Version Summary

| Version | Date       | Type  | Key Changes                                                                                              |
|:--------|:-----------|:------|:---------------------------------------------------------------------------------------------------------|
| 0.4.0   | 2025-07-04 | ✨    | Enhances project stability and maintainability through refactoring, dependency updates, and CI adjustments. |
| 0.3.1   | 2025-07-04 | 🐛    | Fixed CLI output overlap by migrating from `halo` to `rich` for spinners and logging.                    |
| 0.3.0   | 2025-07-03 | Minor | Major refactor to a service-based architecture, with new features and tests.                             |
| 0.2.0   | 2024-06-09 | ✨    | Python package, CLI, modular utilities, Docker/Hub support                                               |
| 0.1.0   | 2025-06-27 | 🎉    | Initial release, porting core features from shell script to a Python package.                            |

## Project Features

- Build, tag, and push Docker images to Docker Hub or GitHub Container Registry
- Python CLI is built with **Click** and mirrors original shell script options, offering enhanced UX and testability
- Refactored configuration into focused dataclasses for clarity and maintainability
- Standardized error handling with custom exceptions for predictable error reporting
- Modular utilities for logging, smart rebuilds, input validation, and cleanup
- Smart rebuild optimization and dry-run support
- Secure token handling and input validation
- Generates config templates (.env, .dockerignore)
- Build-context validation with optimisation suggestions & large-file detection
- User-friendly progress indicator (spinner) powered by `rich` during long-running Docker operations
- Robust dependency checks (docker binary & daemon, system tools)
- Shell script and Python package both supported
- Comprehensive static analysis (Ruff, Black, Pylint, Pydocstyle) and CI/CD pipeline
- BATS-based shell test suite and Pytest-based Python unit tests

## Project Structure

<details><summary>Show tree</summary>

```text
.├── .github/workflows/    # CI/CD workflows
│   └── ci.yml
├── docker_ctp/           # Main Python package
│   ├── cli/              # Click-based CLI entrypoint
│   ├── core/             # Core logic: service layer, Docker ops
│   ├── config/           # Configuration dataclasses
│   ├── exceptions.py     # Custom exception classes
│   └── utils/            # Helper modules
├── tests/                # Pytest suites
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_service.py
│   └── test_utils.py
├── to-do/                # Task-specific refactoring plans
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── pdm.lock
├── pyproject.toml
└── README.md
```

</details>

## Architecture Highlights

The architecture has been refactored to decouple the command-line interface from the core application logic. This was achieved by introducing a **Service Layer** that encapsulates the primary business logic and uses **Dependency Injection** to manage its dependencies.

- **Service-Oriented Design**: The new `DockerService` in `docker_ctp/core/service.py` centralizes the orchestration of Docker operations (build, tag, push). This service acts as the single source of truth for the application's workflow.
- **Dependency Injection**: The `DockerService` receives its dependencies (like `Config`, `Runner`, and `CleanupManager`) via its constructor. This inverts control, making the service easier to test in isolation and more flexible to future changes.
- **Thin CLI Layer**: The `docker_ctp/cli/__init__.py` module is now a lightweight interface responsible only for parsing user input, preparing dependencies, and invoking the `DockerService`.

- [docker_ctp/core/service.py](docker_ctp/core/service.py): The new service layer that orchestrates the build-tag-push workflow.
- [docker_ctp/core/docker_ops.py](https://github.com/beecave-homelab/docker-ctp/blob/f948c2fbf978b7d88e4e6fdb32e6746684526b03/docker_ctp/core/docker_ops.py): High-level Docker build, tag, push logic with error handling.
- [docker_ctp/cli/**init**.py](docker_ctp/cli/__init__.py): A lightweight Click-based CLI that delegates to the `DockerService`.
- [docker_ctp/config/**init**.py](docker_ctp/config/__init__.py): Refactored `Config` class with nested dataclasses and constructors.
- [docker_ctp/exceptions.py](docker_ctp/exceptions.py): Centralized custom exceptions for consistent error reporting.
- [docker-ctp.sh](https://github.com/beecave-homelab/docker-ctp/blob/f948c2fbf978b7d88e4e6fdb32e6746684526b03/docker-ctp.sh): Original shell implementation
- [tests/test_docker_ctp.sh](https://github.com/beecave-homelab/docker-ctp/blob/f948c2fbf978b7d88e4e6fdb32e6746684526b03/tests/test_docker_ctp.sh): BATS test suite
- [pyproject.toml](https://github.com/beecave-homelab/docker-ctp/blob/f948c2fbf978b7d88e4e6fdb32e6746684526b03/pyproject.toml): Project metadata and dependencies

## API
>
> No public HTTP API is implemented in this repository.

## CLI

The command-line interface is built with Click and provides the following options:

| Flag | Alias | Description |
| :--- | :--- | :--- |
| `--banner` | | Show the ASCII art banner and exit. |
| `--username` | `-u` | Registry username. |
| `--image-name` | `-i` | Docker image name. See note below for precedence. |
| `--image-tag` | `-t` | Docker image tag. |
| `--dockerfile-dir` | `-d` | Path to Dockerfile directory. Also used for image name if `-i` is not set. |
| `--registry` | `-g` | Target registry (`docker` or `github`). |
| `--no-cache` | | Disable Docker's build cache. |
| `--force-rebuild` | | Force a rebuild even if a matching image already exists. |
| `--dry-run` | | Simulate all commands without executing them. |
| `--verbose` | | Enable verbose (DEBUG level) output. |
| `--quiet` | | Suppress all informational output (errors only). |
| `--no-cleanup` | | Disable automatic cleanup of intermediate images. |
| `--generate-config` | | Generate default `.env` and `.dockerignore` files and exit. |
| `--version` | | Show the application version and exit. |
| `--help` | | Show this help message and exit. |

**Image Name Precedence:**

The Docker image name is determined using the following priority order:

1. The `--image-name` (`-i`) command-line flag.
2. The `IMAGE_NAME` variable in an `.env` file.
3. The name of the directory specified by `--dockerfile-dir` (`-d`).
4. The name of the current working directory (as a final fallback).

See [docker_ctp/cli/**init**.py](docker_ctp/cli/__init__.py) for the full implementation.

## WebUI
>
> No web user interface is present in this repository.

## Code Quality

- **Static Analysis:**
  - Ruff, Pylint, and Pydocstyle are configured and enforced via PDM scripts and pre-commit hooks, ensuring code quality and style compliance.
  - All imports within the `docker_ctp` package have been standardized to use absolute paths for improved clarity and maintainability.
  - Run checks locally with:
    - `pdm run lint-ruff`
    - `pdm run lint-pylint`
    - `pdm run pydocstyle --convention=google docker_ctp`
- **Continuous Integration:**
  - GitHub Actions workflow in `.github/workflows/ci.yml` runs static analysis and tests (with coverage) on push and pull request to main/dev branches.
  - Ensures all code meets style, lint, documentation, and functional standards before merging.

## Docker

- [Dockerfile](https://github.com/beecave-homelab/docker-ctp/blob/f948c2fbf978b7d88e4e6fdb32e6746684526b03/Dockerfile) present (minimal, based on alpine)
- Supports building and pushing images to Docker Hub and GitHub Container Registry

## Tests

- The BATS test suite for the legacy shell script is no longer maintained.
- [tests/test_cli.py](tests/test_cli.py): Pytest suite for the Click CLI, covering help, version, dry-run scenarios, and completion messages.
- [tests/test_config.py](tests/test_config.py): Pytest suite for the Config class, covering username resolution, default tag selection, and validation.
- [tests/test_service.py](tests/test_service.py): Pytest suite for the `DockerService`, using mocks to test the core logic in isolation.
- [tests/test_utils.py](tests/test_utils.py): Build-context validation and other utility helpers.
- 24 pytest cases cover CLI, Config, Service, Util functions, build-context validation, and error handling – all **passing**.

## Recent Improvements

- ✨ **Architectural Redesign**: Decoupled the CLI from core logic by introducing a `DockerService` layer, using dependency injection for better testability and maintenance.
- ✨ **CI/CD Pipeline**: Implemented a full CI workflow with GitHub Actions to automate testing and linting.
- ✨ **Enhanced Tooling**: Migrated to Click for the CLI, added a progress spinner (`rich`), and implemented pre-commit hooks for code quality.
- 🔧 **Refactoring**: Overhauled configuration management with dataclasses, standardized exceptions, and improved the `.env` loading mechanism.
- 🐛 **Bug Fixes**: Fixed CLI output overlap by migrating from `halo` to `rich`.
- 🐛 **Bug Fixes**: Addressed issues with CLI argument parsing and error handling.
- 🧪 **Testing**: Added a comprehensive `pytest` suite covering the service layer, CLI, configuration, and utilities.

**Always update this file when code or configuration changes.**
