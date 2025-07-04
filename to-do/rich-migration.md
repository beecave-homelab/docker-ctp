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

- [x] **Testing**:
  - [x] Run the CLI with the `--dry-run` flag to test the new output.
  - [x] Verify that there is no overlapping text and that all messages are displayed correctly.

- [x] **Documentation**:
  - [x] Update `project-overview.md` to reflect the dependency changes and any other relevant modifications.
