# Plan: Migrate from Halo to Rich

## Rationale

The `halo` library is causing issues with overlapping output because it does not support logging while a spinner is active. The library is also unmaintained. Migrating to `rich` will resolve these issues and provide a more robust and modern CLI experience.

## Task List

- [x] **Update Dependencies**:
  - [x] In `pyproject.toml`, remove `halo` from the dependencies.
  - [x] Add `rich` to the dependencies in `pyproject.toml`.

- [x] **Refactor Logging and Spinners**:
  - [x] In `docker_ctp/utils/logging_utils.py`, replace `halo` with `rich.status` for spinners.
  - [x] Update the `MessageHandler` class to use `rich.console.Console` for all output, ensuring that messages do not interfere with the spinner.

- [x] **Improve Logging Output**:
  - [x] In `docker_ctp/cli/__init__.py`, configure logging to use `rich.logging.RichHandler` for cleaner and more readable output.

- [x] **Single Source of Truth Logger Setup**:
  - [x] Add `configure(verbose=False, quiet=False)` helper in `docker_ctp/utils/logging_utils.py` that installs `rich.logging.RichHandler` on the root logger and sets the level based on the flags.
  - [x] Ensure the helper is idempotent (does not add duplicate handlers on repeated calls).
  - [x] Update `docker_ctp/cli/__init__.py` to call `configure(verbose, quiet)` before any logging occurs.

- [x] **Centralise Logging Calls**:
  - [x] Replace direct `import logging` statements in all modules (`build_context.py`, `config_generation.py`, `input_validation.py`, `runner.py`, `config/__init__.py`) with imports from `docker_ctp.utils.logging_utils` or ensure they rely on the root logger configured with `RichHandler`.
  - [x] Route user-visible output through `MessageHandler` (`get_message_handler().info/warning/error/success`).
  - [x] Add/adjust unit tests to verify Rich-formatted logs and non-overlapping spinner output.

- [x] **Testing**:
  - [x] Run the CLI with the `--dry-run` flag to test the new output.
  - [x] Verify that there is no overlapping text and that all messages are displayed correctly.

- [x] **Documentation**:
  - [x] Update `project-overview.md` to reflect the dependency changes and any other relevant modifications.
