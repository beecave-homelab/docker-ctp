# Debugging Test Failures

## Investigation Plan

- [x] Analyze test failures from the user's input.
- [x] Read `tests/test_cli.py` to understand why the CLI tests are failing.
- [x] Read `tests/test_service.py` to understand why the service layer tests are failing.
- [x] Fix the assertion in `tests/test_service.py` to align with the updated `docker_ops.login` function signature.
  > **Result**: Corrected the mock calls for `docker_ops.login` and `docker_ops.push` to match their new signatures.
- [x] Investigate and fix the `TypeError` in `tests/test_cli.py`. The error `Config.__init__() got an unexpected keyword argument 'dry_run'` is strange because the `Config` class does have a `dry_run` attribute. This requires a deeper look into how `click` is passing arguments.
  > **Result**: Fixed the `TypeError` by explicitly mapping CLI `kwargs` to the `Config` dataclass fields. This ensures no unexpected arguments are passed to the constructor.
