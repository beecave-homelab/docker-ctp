# docker-ctp

A Python-based tool for building, tagging, and pushing Docker images to Docker Hub or GitHub Container Registry. This project is a modern reimplementation of the original `docker-ctp.sh` shell script, providing a robust CLI and modular Python codebase for container workflows.

## Versions

**Current version**: 0.1.0 – Initial Python implementation with CLI mirroring the original shell script, modular utilities, and support for both Docker Hub and GitHub Container Registry.

## Table of Contents

- [Versions](#versions)
- [Badges](#badges)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)

## Badges

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-supported-blue)

## Installation

- **Preferred:** Install via pipx (recommended for isolated CLI tools):

  ```bash
  pipx install "git+https://github.com/beecave-homelab/docker-ctp.git"
  ```

- **Alternative:** Install with PDM (for development or editable installs):

  ```bash
  pdm install

  # with lint and testing dependencies
  pdm install --group lint,test
  ```

- **Shell Script:** To install the original shell script helper:

  ```bash
  ./install.sh
  ```

  Use the `--dry-run` flag to preview actions without making changes.

## Usage

The command line interface mirrors the original shell script:

```bash
python -m docker_ctp.cli [OPTIONS]
```

**Key options:**

- `-u`, `--username` – registry username
- `-i`, `--image-name` – image name
- `-t`, `--image-tag` – image tag
- `-d`, `--dockerfile-dir` – path to the Dockerfile directory
- `-g`, `--registry` – `docker` or `github` (default: docker)
- `--dry-run` – print commands without running them
- `--verbose` – verbose logging
- `--quiet` – suppress non-error output

Environment variables from a `.env` file or the environment can define default values. Authentication uses `DOCKER_TOKEN` or `GITHUB_TOKEN` depending on the registry.

A sample `.env.example` file is provided. Copy it to `.env` and adjust values as needed.

## License

This project is licensed under the MIT license. See [LICENSE](LICENSE) for more information.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
