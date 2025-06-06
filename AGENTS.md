# Guidelines for docker-ctp

This repository contains a small Python package that replicates the
behaviour of an earlier shell script (`docker-ctp.sh`) used to build, tag
and push Docker images. The shell script itself is not present; instead
`docker_ctp` provides a command line interface implemented in Python.

## Repository structure

```
docker_ctp/         Python package
├── __init__.py     Package version
├── cli.py          Command line interface
├── config.py       Dataclass for configuration and environment loading
├── docker_ops.py   Docker login/build/tag/push helpers
└── runner.py       Utility to run shell commands

install.sh          Optional installer for the original shell helper
.env.example        Sample environment file
requirements-test.txt  Linting and test dependencies
TESTING.md          Describes how to run checks
```

## Usage overview

Run the CLI using:

```bash
python -m docker_ctp.cli [OPTIONS]
```

Options include registry selection (`docker` or `github`), image name and
tag, Dockerfile directory, and flags for cache, dry-run, verbose or quiet
output. Environment variables may be loaded from `.env` or other standard
locations (see `docker_ctp.config`). Authentication tokens are required:
`DOCKER_TOKEN` for Docker Hub or `GITHUB_TOKEN` for the GitHub Container
Registry.

## Testing

The project relies on the tools listed in `requirements-test.txt`. To run
all checks:

1. Create and activate a virtual environment.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-test.txt
   ```

2. Run static analysis and type checking.

   ```bash
   isort --profile black --check --diff docker_ctp
   black --check docker_ctp
   ruff check docker_ctp
   mypy docker_ctp
   pydocstyle docker_ctp
   pylint docker_ctp
   ```

3. Execute unit tests.

   ```bash
   pytest --cov=docker_ctp --cov-report=term-missing
   ```

The repository currently has no tests. Create a `tests` directory and add
files named `test_*.py`. When testing functions that interact with the
Docker CLI, use mocking to avoid running real Docker commands.
