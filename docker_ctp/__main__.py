"""Run docker-ctp as a module."""

import sys

from .main import main

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
