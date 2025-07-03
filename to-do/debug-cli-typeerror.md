# Debugging CLI TypeError

## Investigation Plan

- [x] Analyze the new `TypeError` from the user's input. The error has shifted from an unexpected `dry_run` argument to an unexpected `registry` argument.
- [x] Re-read `docker_ctp/config.py` to confirm the `Config` class definition is correct and includes a `registry` attribute.
- [x] Re-read `docker_ctp/cli/__init__.py` to meticulously review how the `config_params` dictionary is constructed and passed to the `Config` constructor.
- [x] Formulate a hypothesis for the root cause. The continued `TypeErrors` suggest a fundamental issue with how `click` options are being collected into `**kwargs` and then mapped to the `Config` object.
- [x] Develop and apply a fix.
  > **Result**: Fixed the recurring `TypeError` by refactoring the `config_params` creation to use a dictionary comprehension that introspects the `Config` class annotations. This ensures only valid arguments are ever passed to the constructor. Also added `dest="tag"` to the `image-tag` option for consistency.
