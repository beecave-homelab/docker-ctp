# docker-ctp

This package provides a Python implementation of the original `docker-ctp.sh`
script. It builds, tags and pushes Docker images to Docker Hub or the GitHub
Container Registry.

## Usage

The command line interface mirrors the shell script:

```bash
python -m docker_ctp.cli [OPTIONS]
```

### Package Modules

- `docker_ctp.config` – configuration dataclass and environment loading
- `docker_ctp.runner` – helper for running shell commands
- `docker_ctp.docker_ops` – docker build, tag and push functions
- `docker_ctp.cli` – command line interface

Key options:

- `-u`, `--username` – registry username.
- `-i`, `--image-name` – image name.
- `-t`, `--image-tag` – image tag.
- `-d`, `--dockerfile-dir` – path to the Dockerfile directory.
- `-g`, `--registry` – `docker` or `github` (default: docker).
- `--dry-run` – print commands without running them.
- `--verbose` – verbose logging.
- `--quiet` – suppress non-error output.

Environment variables from a `.env` file or the environment can define default
values. Authentication uses `DOCKER_TOKEN` or `GITHUB_TOKEN` depending on the
registry.

## Configuration

A sample `.env.example` file is provided with the most common options. Copy it
to `.env` and adjust the values to suit your environment.

## Installing the shell helper

Although this repository contains a Python version, a helper `install.sh`
script is included for users who want to install the original shell script to
`/usr/local/bin`. Run the installer with:

```bash
./install.sh
```

Use the `--dry-run` flag to preview the actions without making any changes.
