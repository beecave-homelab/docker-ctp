# Release History

This file documents all notable changes to the `docker-ctp` project. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## **v0.3.0** (Current) - *03-07-2025*

✨ **Architectural Overhaul, Feature Enhancements & Testing**

### ✨ **New Features in 0.3.0**

- **Added**: Service layer (`DockerService`) to abstract Docker build/push logic from the CLI.
- **Added**: Progress spinner for long-running Docker operations.
- **Added**: CI workflow for automated testing.

### 🔧 **Improvements in 0.3.0**

- **Refactored**: Decoupled CLI from core application logic using a service-based architecture.
- **Refactored**: Enhanced build context validation and `.env` file handling.
- **Refactored**: Centralized configuration and CLI initialization.
- **Enhanced**: Logging configuration and output.

### 🧪 **Tests in 0.3.0**

- **Added**: Unit tests for the new `DockerService`.
- **Added**: Comprehensive tests for Docker CLI interactions and utility functions.

### 📝 **Documentation in 0.3.0**

- **Added**: Architectural design documents for the refactor.
- **Updated**: Project overview and README to reflect the new architecture.

#### 📝 **Commits in 0.3.0**: `f948c2f`, `506cbd1`, `651863c`, `1e3c766`, `8b6a515`, `888643f`, `1e9479f`, `4f05a5b`, `728380b`, `bac810c`, `3f5274e`, `dc487c7`, `df4d04a`, `2319023`, `6756975`, `9a485a4`, `020dcea`, `955ec9e`, `a3aa4e5`, `0ba2f03`, `ca78044`, `a7e7f55`

---

## **v0.2.0** - *27-06-2025*

✨ **Configuration Refactor, Validation & DX Improvements**

This release focuses on refactoring the configuration generation, improving build context validation, and enhancing the developer experience with progress spinners and better logging.

### 🔧 Improvements in v0.2.0

- **Refactored**: Enhanced build context validation and configuration generation logic for more robust builds.
- **Refactored**: Improved Docker operations with an interactive progress spinner for better user feedback during long-running tasks.
- **Refactored**: Enhanced `.env` file loading and validation to ensure required variables are present.
- **Refactored**: Simplified `exceptions.py` by removing redundant docstrings.

### 🧪 Tests in v0.2.0

- **Added**: Comprehensive tests for Docker CLI interactions and core utility functions to ensure reliability.

### 📝 Documentation in v0.2.0

- **Updated**: Refactored `config_params` creation documentation for clarity.
- **Updated**: The `project-overview.md` was updated to reflect the latest changes and include build-context validation details.

### 📦 Maintenance in v0.2.0

- **Added**: New dependencies and updated testing-related packages.
- **Updated**: Logging configuration and CLI generation for better maintainability.
- **Fixed**: Removed a deleted file from `docker_ctp/__init__.py`.

#### 📝 **Commits in v0.2.0**: `f948c2f`, `506cbd1`, `651863c`, `1e3c766`, `8b6a515`, `888643f`, `1e9479f`, `4f05a5b`, `728380b`, `bac810c`

---

## **v0.1.0** - *27-06-2025*

🎉 **Initial Release: Port to Python Package**

This was the first official release of `docker-ctp` as a Python package, migrating from the original `docker-ctp.sh` script. The core functionality of building, tagging, and pushing Docker images was ported and expanded.

### ✨ New Features in v0.1.0

- **Added**: Core functionality ported to a structured Python package with subpackages.
- **Added**: Initial Docker configuration files and testing scripts.

### 📝 Documentation in v0.1.0

- **Added**: A detailed `README.md` with a project overview and versioning information.
- **Added**: A `TESTING.md` guide and requirements for testing and code quality.

### 📦 Maintenance in v0.1.0

- **Added**: Initial commit and project structure.
- **Updated**: The `Dockerfile` to conditionally use an Alpine base image for smaller builds.
- **Updated**: `.gitignore` to include tool-specific files.

#### 📝 **Commits in v0.1.0**: `cf68fef`, `b8f5f81`, `2012677`, `60c0d89`, `6e76882`, `ab5106b`, `ee3fce8`, `85015ee`, `a3005d9`, `b8f0709`

---
