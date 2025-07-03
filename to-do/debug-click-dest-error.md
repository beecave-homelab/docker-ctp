# Debugging Click `dest` Argument Error

## Investigation Plan

- [x] Analyze the `TypeError` from the user's input during test collection.
- [x] The error `TypeError: Parameter.__init__() got an unexpected keyword argument 'dest'` points to a misconfiguration in a `click.option` decorator.
- [x] The root cause is providing both a positional argument for the destination (`"tag"`) and the `dest="tag"` keyword argument simultaneously. The positional argument is sufficient.
- [x] I will remove the redundant `dest="tag"` from the `--image-tag` option in `docker_ctp/cli/__init__.py`.
  > **Result**: Removed the `dest="tag"` keyword argument from the `@click.option` decorator, which resolved the `TypeError` during test collection.

- [x] Analyze the new `TypeError: ... unexpected keyword argument 'use_cache'`.
- [x] The dynamic mapping from `click`'s `kwargs` to the `Config` parameters is still the root cause of the problem.
- [x] Replace the dictionary comprehension with an explicit, manual mapping of parameters. This will guarantee that no unexpected keyword arguments are ever passed to the `Config` constructor.
  > **Result**: Replaced the brittle parameter mapping with an explicit, verbose mapping. This correctly constructs the arguments for the `Config` dataclass and resolves the recurring `TypeError`.

- [x] Analyze the new `TypeError: ... unexpected keyword argument 'registry'`.
  > **Result**: The error was caused by an incomplete refactoring. A new `docker_ctp/config/__init__.py` introduced a nested `Config` object, but an old, untracked `docker_ctp/config.py` with a flat structure was still present. Pytest was importing the new, nested `Config`, but the CLI was written to instantiate the old, flat one, causing a `TypeError`. The same issue existed for `cli.py`, `runner.py`, and `docker_ops.py`. I deleted the stale files and updated `docker_ctp/cli/__init__.py` to use the `Config.from_cli` factory method, which correctly handles the new nested configuration structure.
- [x] Run the tests again to confirm the fix.
  > **Result**: The tests failed during collection with an `ImportError`. The refactoring left incorrect absolute imports in `docker_ctp/core/service.py`.
- [x] Fix the imports in `docker_ctp/core/service.py` to use relative imports.
  > **Result**: Corrected the import statements in `docker_ctp/core/service.py` to use relative paths, resolving the `ImportError`.
- [x] Fix `login` and `push` calls in `docker_ctp/core/service.py`.
  > **Result**: The test failure `TypeError: login() missing 1 required positional argument: 'runner'` was caused by incorrect arguments. The calls to `docker_ops.login` and `docker_ops.push` were updated to provide the required `runner` and `config` arguments.
- [x] Update assertions in `tests/test_service.py`.
  > **Result**: The test `test_execute_workflow` was failing because the mock assertions for `docker_ops.login` and `docker_ops.push` were outdated. I updated the assertions to match the new function signatures.
- [x] Run the final tests.
  > **Result**: All 13 tests passed. The refactoring issues are resolved.
