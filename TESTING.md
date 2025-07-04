# Testing Plan

This repository includes a minimal Python package, `docker_ctp`. The
`pyproject.toml` file lists the tools used for testing and code quality.
The following sections describe how to set up the environment and run all
checks.

## 1. Installation

Create a virtual environment and install the test dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pdm install
```

## 2. Static Analysis and Formatting

The project uses several linters and formatters. Run them before running the
unit tests:

```bash
# Ensure imports and code style
isort --check --diff docker_ctp  # add tests/ if created

# Ruff provides additional linting
ruff check docker_ctp

# Type checking
mypy docker_ctp

# Docstring style
pydocstyle docker_ctp

# General linting
pylint docker_ctp
```

Apply `isort` without the `--check` flag to automatically format files if necessary.
## 3. Running the Unit Tests

Tests are written with `pytest` and coverage reporting is provided by
`pytest-cov`:

```bash
pytest --cov=docker_ctp --cov-report=term-missing
```
If present, this command will execute all tests under the `tests` directory and display a coverage summary highlighting lines that are not executed.

## 4. Writing Tests

Currently the repository does not include any tests; create the `tests` directory and add `test_*.py` files as needed.
Place new tests inside the `tests` directory. Name files using the pattern
`test_*.py` so that `pytest` can discover them automatically. Aim to cover both
normal usage and failure cases for public functions such as:

- `docker_ctp.runner.Runner`
- `docker_ctp.config` helpers (`load_env`, `validate_config`, etc.)
- `docker_ctp.docker_ops`
- The command line interface in `docker_ctp.cli`

Tests should avoid performing real Docker operations. Use mocking (e.g.
`unittest.mock`) to simulate calls to the Docker CLI.

## 5. Continuous Integration

Integrate the above checks in your CI configuration to ensure commits meet the
project's quality standards. A typical CI job would run the commands from the
Static Analysis and Unit Tests sections.

