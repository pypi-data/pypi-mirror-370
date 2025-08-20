"""Tests for configuration loader error and no-file branches."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ties._configuration import load_config

if TYPE_CHECKING:
    from pathlib import Path


def test_load_config_no_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With no config files present, an empty dict is returned."""
    monkeypatch.chdir(tmp_path)
    assert load_config() == {}


def test_load_config_invalid_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invalid TOML triggers an error message and SystemExit with ERROR code."""
    bad = tmp_path / "pyproject.toml"
    bad.write_text("this is : not toml", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        load_config()
