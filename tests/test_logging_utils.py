"""Unit tests for centralized logging utilities and Rich configuration."""

from __future__ import annotations

import logging
from typing import List

import pytest
from rich.logging import RichHandler

from docker_ctp.utils.logging_utils import configure, get_message_handler


def _reset_root_logger() -> None:
    """Remove all handlers and reset the root logger level.

    Each test manipulates the root logger state via *configure()*; we must reset
    it to guarantee isolation and avoid handler leakage across tests.
    """
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.NOTSET)


@pytest.fixture(autouse=True)
def _isolate_root_logger() -> None:  # noqa: D401
    """Automatically reset the root logger before each test."""
    _reset_root_logger()
    yield
    _reset_root_logger()


def _rich_handlers() -> List[RichHandler]:
    """Return a list of RichHandler instances currently attached to root."""
    return [h for h in logging.getLogger().handlers if isinstance(h, RichHandler)]


# ---------------------------------------------------------------------------
# configure() behaviour
# ---------------------------------------------------------------------------


def test_configure_installs_single_rich_handler() -> None:  # noqa: D401
    """configure() should add exactly one RichHandler, even when called twice."""
    configure()  # first call
    configure(verbose=True)  # second call should be a no-op
    assert len(_rich_handlers()) == 1


def test_configure_quiet_sets_error_level() -> None:  # noqa: D401
    """The *quiet* flag should raise the root logger level to ERROR."""
    configure(quiet=True)
    assert logging.getLogger().level == logging.ERROR


# ---------------------------------------------------------------------------
# MessageHandler behaviour
# ---------------------------------------------------------------------------


def test_message_handler_info_emits_log(caplog):  # noqa: D401
    """messages.info() should emit an INFO level log captured by *caplog*."""
    configure()
    messages = get_message_handler()
    with caplog.at_level(logging.INFO):
        messages.info("hello world")
    assert "hello world" in caplog.text
