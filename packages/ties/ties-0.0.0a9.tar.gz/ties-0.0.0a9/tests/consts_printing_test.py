"""Tests for `ties._consts.cprint` with and without TTY."""

from __future__ import annotations

from typing import Any

from ties import _consts


def test_cprint_non_tty(monkeypatch: Any, capsys: Any) -> None:
    """When not a TTY, plain text is printed without ANSI codes."""
    monkeypatch.setattr(_consts, "IS_TTY", False, raising=True)
    _consts.cprint("hello", color=_consts.Colors.GREEN, bold=True)
    out = capsys.readouterr().out
    assert out.strip() == "hello"


def test_cprint_tty(monkeypatch: Any, capsys: Any) -> None:
    """When TTY, ANSI color and style sequences are included in output."""
    monkeypatch.setattr(_consts, "IS_TTY", True, raising=True)
    _consts.cprint("hello", color=_consts.Colors.GREEN, bold=True)
    out = capsys.readouterr().out
    # Should contain color and bold sequences
    assert _consts.Colors.GREEN in out
    assert _consts.Colors.BOLD in out
    assert _consts.Colors.END in out
