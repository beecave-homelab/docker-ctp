# Fix pylint issues in docker_ctp.cli.__init__.py

## Checklist

- [x] Swap except clause order to fix E0701 (CLIError before ClickException).
- [x] Prefix Click exception classes with `click.` to fix E0602.
- [x] Rename unused argument `param` -> `_param` in `print_banner` to fix W0613.
- [x] Narrow broad `except Exception` (W0718) – added pylint disable comment.
- [x] Converted `elif` after return into separate `if` (R1705) – already resolved.
- [x] Import order adjusted; no C0411/C0415 warnings remain.
