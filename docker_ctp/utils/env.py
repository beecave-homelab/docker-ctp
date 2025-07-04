"""Environment variable utilities."""

from __future__ import annotations

import os
from typing import TypeVar, overload

T = TypeVar("T")


@overload
def get_env(key: str) -> str | None: ...


@overload
def get_env(key: str, default: T) -> str | T: ...


def get_env(key: str, default: T | None = None) -> str | T | None:
    """Retrieve an environment variable with an optional default.

    Args:
        key: The name of the environment variable.
        default: The default value to return if the variable is not set.

    Returns:
        The value of the environment variable, or the default value.
    """
    return os.environ.get(key, default)
