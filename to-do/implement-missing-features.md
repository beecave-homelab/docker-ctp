# To-Do: Implement Missing Features from Bash Script

This plan outlines the steps to implement the remaining functionality from the `docker-ctp.sh` script into the `docker_ctp` Python package to achieve full feature parity.

## Tasks

- [x] **Analysis Phase:**
  - [X] A thorough code review has been completed, and the gaps between the shell script and the Python package have been identified. No further analysis is needed.

- [x] **Implementation Phase:**
  - [X] **1. Implement Build Context Validation**
    - **Path:** `docker_ctp/utils/build_context.py`
    - **Action:** Replicate the shell script's logic for validating the build context. This includes:
      - Checking for the existence and readability of `.dockerignore`.
      - Warning about potentially problematic patterns (e.g., `**`).
      - Scanning for common excludable files/directories (e.g., `.git`, `node_modules`, `tests`).
      - Detecting and warning about large files (>50MB) in the build context.
    - **Acceptance Criteria:** The function should log warnings and optimization suggestions to the console, mirroring the behavior of the original script.

  - [X] **2. Implement Configuration File Generation**
    - **Path:** `docker_ctp/utils/config_generation.py`
    - **Action:** Implement the logic to generate a default `.env` file and a `.dockerignore` template. This must include:
      - Creating the user config directory (`~/.config/docker-ctp/`) if it doesn't exist.
      - Writing the default `.env` content to `~/.config/docker-ctp/.env`, avoiding overwrites.
      - Writing the `.dockerignore` template to the current working directory, avoiding overwrites.
    - **Acceptance Criteria:** Running the CLI with `--generate-config` produces the expected files in their correct locations with content identical to the script's output.

  - [X] **3. Enhance Dependency Checking**
    - **Path:** `docker_ctp/utils/dependency_checker.py`
    - **Action:** Improve the dependency checker to fully match the script's capabilities.
      - Verify that the `docker` executable is available in the system's `PATH`.
      - Check if the Docker daemon is running and responsive (this check should be skipped in `--dry-run` mode).
    - **Acceptance Criteria:** The application exits gracefully with an informative error message if Docker is not installed or the daemon is not running.

  - [X] **4. Implement .env File Loading Logic**
    - **Path:** `docker_ctp/config/__init__.py`
    - **Action:** Update the `load_env` function to search for the `.env` file in multiple locations, following the same priority order as the shell script:
      1. `./.env` (only if the current directory is `docker-ctp`)
      2. `$HOME/.config/docker-ctp/.env`
      3. `$HOME/.docker-ctp/.env`
      4. `/etc/docker-ctp/.env`
    - **Acceptance Criteria:** The application correctly finds and loads the `.env` file from the first location in the priority list where it exists.

  - [X] **5. Add User-Friendly Progress Indicator**
    - **Path:** `docker_ctp/core/runner.py` and `docker_ctp/core/docker_ops.py`
    - **Action:** Implement a visual progress indicator (e.g., a spinner or animated dots) that is displayed during long-running Docker operations.
      - The `Runner` class should be enhanced to manage the lifecycle of the progress indicator around subprocess calls.
      - The `docker_ops.build` and `docker_ops.push` functions will need to invoke this new functionality from the runner.
    - **Acceptance Criteria:** A progress indicator is shown during the `build` and `push` steps to provide better UX, similar to the `show_progress` function in the script.

- [x] **Testing Phase:**
  - [x] **Unit / Integration Tests**
    - **Path:** `tests/`
    - **Action:** Write tests for all the newly implemented or modified utility functions to ensure they behave as expected.
    - **Acceptance Criteria:** The test suite passes, and code coverage is maintained or improved.

- [x] **Debugging Phase**
  - **Symptom:** The test suite fails with multiple errors after implementing new features and adding corresponding tests.
  - **Steps Taken:**
    - **Dependency Errors:** Resolved a `ModuleNotFoundError` for the `halo` package by running `pdm install` to sync the test environment's dependencies.
    - **Import Errors:** Fixed a `NameError` by adding a missing `import subprocess` in `tests/test_utils.py`. Fixed an `ImportError` by removing the import for the deleted `validate_config` function in `tests/test_config.py`.
    - **Configuration Logic:** Refactored the `docker_ctp/config/__init__.py`'s `load_env` function to improve how it updates configuration from `.env` files. This fix appears to be incomplete as related tests are still failing.
    - **Validation Logic:** Centralized all input validation from the now-deleted `validate_config` function into the `DockerService._validate_inputs` method. This ensures validation runs as part of the main application workflow.
    - **Test Cleanup:** Removed obsolete tests for the `validate_config` function from `tests/test_config.py`.
  - **Current Status:** All tests pass (24/24). Configuration loading, CLI exception handling, and DockerService initialization issues resolved.

- [x] **Documentation Phase:**
  - [x] **Update Project Overview**
    - **Path:** `project-overview.md`
    - **Action:** Ensure the project overview documentation is updated to reflect the new capabilities of the Python package, confirming it has reached full feature parity with the original script.
    - **Acceptance Criteria:** The documentation is accurate and complete.

## Related Files

- `docker_ctp/utils/build_context.py`
- `docker_ctp/utils/config_generation.py`
- `docker_ctp/utils/dependency_checker.py`
- `docker_ctp/config/__init__.py`
- `docker_ctp/core/runner.py`
- `docker_ctp/core/docker_ops.py`
