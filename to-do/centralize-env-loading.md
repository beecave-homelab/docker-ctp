# To-Do: Centralize Environment Variable Loading

**Objective:** Refactor the codebase to use a single, centralized utility for accessing environment variables. This will improve maintainability, consistency, and make future modifications easier.

## Task Breakdown

### 1. Create a Centralized Environment Utility

- [x] Create a new file: `docker_ctp/utils/env.py`.
- [x] Add an `__init__.py` file to the `utils` directory if it doesn't exist to ensure it's treated as a package.
- [x] Define a helper function `get_env(key: str, default: T | None = None)` in `docker_ctp/utils/env.py`. This function will wrap `os.environ.get()`.

### 2. Refactor Existing Code

- [x] **`docker_ctp/config/__init__.py`**:
  - [x] Import `get_env` from `docker_ctp.utils.env`.
  - [x] Replace all instances of `os.environ.get()` with calls to the new `get_env()` helper function.

- [x] **`docker_ctp/utils/auth.py`**:
  - [x] Import `get_env` from `docker_ctp.utils.env`.
  - [x] Replace all instances of `os.environ.get()` with calls to the new `get_env()` helper function.

### 3. Verification

- [x] After refactoring, run any existing tests to ensure that the application's behavior remains unchanged.
- [x] Manually test the CLI to confirm that configuration is still loaded correctly from environment variables.

## Notes

- Encountered and resolved a minor indentation error in `docker_ctp/utils/auth.py` during the refactoring process.
