"""Authentication utilities."""

from __future__ import annotations

import os
from getpass import getpass
from ..exceptions import AuthError

TOKEN_ENVS = {
    "docker": ["DOCKER_TOKEN", "DOCKER_PASSWORD"],
    "github": ["GITHUB_TOKEN", "GHCR_TOKEN"],
}


def get_token(registry: str) -> str:
    """Retrieve authentication token from environment or prompt."""
    for env in TOKEN_ENVS.get(registry, []):
        token = os.environ.get(env)
        if token:
            return token
    if os.isatty(0):  # pragma: no cover - interactive
        return getpass(f"Enter {registry} token: ")
    raise AuthError(f"Environment variable {TOKEN_ENVS[registry][0]} not set")
