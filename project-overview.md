---
repo: https://github.com/beecave-homelab/docker-ctp.git
commit: 2012677c53542d85c019fd307636c100531d6ec0
generated: 2025-07-03T00:00:00Z
---
<!-- SECTIONS:API,CLI,WEBUI,CI,DOCKER,TESTS -->

# Project Overview | docker-ctp

A Python-based tool and shell script for building, tagging, and pushing Docker images to Docker Hub or GitHub Container Registry. Designed for developers and CI/CD workflows needing reproducible container builds.

[![Language](https://img.shields.io/badge/Python-3.13.5-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.2.0-brightgreen)](#version-summary)
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

| Version | Date | Type | Key Changes |
|---|---|---|----|
| 0.2.0 | 2024-06-09 | ✨ | Python package, CLI, modular utilities, Docker/Hub support |

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
- User-friendly progress indicator (spinner) during long-running Docker operations
- Robust dependency checks (docker binary & daemon, system tools)
- Shell script and Python package both supported
- Comprehensive static analysis (Ruff, Black, Pylint, Pydocstyle) and CI/CD pipeline
- BATS-based shell test suite and Pytest-based Python unit tests

## Project Structure

<details><summary>Show tree</summary>

```text
.
├── docker_ctp/           # Main Python package
│   ├── cli/              # Click-based CLI entrypoint and main workflow
│   ├── core/             # Docker logic (build, tag, push)
│   │   ├── docker_ops.py
│   │   └── service.py    # Service layer for core application logic
│   ├── config/           # Refactored Config dataclasses and env loading
│   ├── exceptions.py     # Custom exception classes for standardized error handling
│   ├── utils/            # Utilities: logging, rebuild, validation, etc.
│   ├── main.py           # Entrypoint
│   └── __main__.py       # Entrypoint
├── docker-ctp.sh         # Original shell script
├── install.sh            # Shell script installer
├── src/docker_ctp/       # Packaging stub
├── tests/                # Test scripts (BATS and Pytest)
│   ├── __init__.py       # Python test package initializer
│   ├── test_cli.py       # Pytest suite for CLI
│   ├── test_config.py    # Pytest suite for Config
│   ├── test_service.py   # Pytest suite for the DockerService
│   ├── test_docker_ctp.sh  # BATS suite for shell script
│   └── test_smart_rebuild.sh # BATS suite for smart rebuild
├── to-do/                # Refactoring and improvement plans
├── Dockerfile            # Minimal Dockerfile
├── pyproject.toml        # Project metadata
├── README.md             # User documentation
└── project-overview.md   # (This file)
```

</details>

## Architecture Highlights

The architecture has been refactored to decouple the command-line interface from the core application logic. This was achieved by introducing a **Service Layer** that encapsulates the primary business logic and uses **Dependency Injection** to manage its dependencies.

- **Service-Oriented Design**: The new `DockerService` in `docker_ctp/core/service.py` centralizes the orchestration of Docker operations (build, tag, push). This service acts as the single source of truth for the application's workflow.
- **Dependency Injection**: The `DockerService` receives its dependencies (like `Config`, `Runner`, and `CleanupManager`) via its constructor. This inverts control, making the service easier to test in isolation and more flexible to future changes.
- **Thin CLI Layer**: The `docker_ctp/cli/__init__.py` module is now a lightweight interface responsible only for parsing user input, preparing dependencies, and invoking the `DockerService`.

- [docker_ctp/core/service.py](docker_ctp/core/service.py): The new service layer that orchestrates the build-tag-push workflow.
- [docker_ctp/core/docker_ops.py](https://github.com/beecave-homelab/docker-ctp/blob/2012677c53542d85c019fd307636c100531d6ec0/docker_ctp/core/docker_ops.py): High-level Docker build, tag, push logic with error handling.
- [docker_ctp/cli/**init**.py](docker_ctp/cli/__init__.py): A lightweight Click-based CLI that delegates to the `DockerService`.
- [docker_ctp/config/**init**.py](docker_ctp/config/__init__.py): Refactored `Config` class with nested dataclasses and constructors.
- [docker_ctp/exceptions.py](docker_ctp/exceptions.py): Centralized custom exceptions for consistent error reporting.
- [docker-ctp.sh](https://github.com/beecave-homelab/docker-ctp/blob/2012677c53542d85c019fd307636c100531d6ec0/docker-ctp.sh): Original shell implementation
- [tests/test_docker_ctp.sh](https://github.com/beecave-homelab/docker-ctp/blob/2012677c53542d85c019fd307636c100531d6ec0/tests/test_docker_ctp.sh): BATS test suite
- [pyproject.toml](https://github.com/beecave-homelab/docker-ctp/blob/2012677c53542d85c019fd307636c100531d6ec0/pyproject.toml): Project metadata and dependencies

## API
>
> No public HTTP API is implemented in this repository.

## CLI

- Python CLI: `python -m docker_ctp.cli [OPTIONS]`
- **Click-based CLI** mirrors all major shell script options (username, image name, tag, registry, dry-run, verbose, etc.)
- Provides comprehensive input validation and standardized error handling using custom exceptions.
- Generates config files with `--generate-config`
- See [docker_ctp/cli/**init**.py](docker_ctp/cli/__init__.py)

## WebUI
>
> No web user interface is present in this repository.

## Code Quality

- **Static Analysis:**
  - Ruff, Black, Pylint, and Pydocstyle are configured and enforced via PDM scripts and pre-commit hooks, ensuring code quality and style compliance.
  - Run checks locally with:
    - `pdm run lint-ruff`
    - `pdm run lint-black`
    - `pdm run lint-pylint`
    - `pdm run pydocstyle --convention=google docker_ctp`
- **Continuous Integration:**
  - GitHub Actions workflow in `.github/workflows/ci.yml` runs static analysis and tests (with coverage) on push and pull request to main/dev branches.
  - Ensures all code meets style, lint, documentation, and functional standards before merging.

## Docker

- [Dockerfile](https://github.com/beecave-homelab/docker-ctp/blob/2012677c53542d85c019fd307636c100531d6ec0/Dockerfile) present (minimal, based on alpine)
- Supports building and pushing images to Docker Hub and GitHub Container Registry

## Tests

- [tests/test_docker_ctp.sh](https://github.com/beecave-homelab/docker-ctp/blob/2012677c53542d85c019fd307636c100531d6ec0/tests/test_docker_ctp.sh): BATS-based shell test suite
- [tests/test_cli.py](tests/test_cli.py): Pytest suite for the Click CLI, covering help, version, dry-run scenarios, and completion messages.
- [tests/test_config.py](tests/test_config.py): Pytest suite for the Config class, covering username resolution, default tag selection, and validation.
- [tests/test_service.py](tests/test_service.py): Pytest suite for the `DockerService`, using mocks to test the core logic in isolation.
- [tests/test_utils.py](tests/test_utils.py): Build-context validation and other utility helpers.
- 24 pytest cases cover CLI, Config, Service, Util functions, build-context validation, and error handling – all **passing**.

## Recent Improvements

- Decoupled core application logic from the CLI by introducing a `DockerService` layer and using dependency injection.
- Refactored configuration into modular dataclasses and standardized error handling with custom exceptions.
- Migrated CLI to Click for improved user experience, testability, and type hinting.
- Added build-context validator replicating shell logic.
- Added spinner-based progress indicator around build/push.
- Refined `.env` loading precedence to honour CLI overrides; added search-path tests.
- Implemented full pytest suite (24 tests) achieving 100 % pass rate.
- Implemented comprehensive static analysis pipeline and robust CI/CD workflow with GitHub Actions.

**Always update this file when code or configuration changes.**
