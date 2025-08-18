"""Tests for `ties.common_transforms` coverage."""

import os

from ties.common_transforms import embed_environ


def test_embed_environ_replaces_and_missing() -> None:
    """Environment placeholders are replaced; unknown variables become empty."""
    os.environ["X"] = "42"
    try:
        text = "value=${env:X}; none=${env:NOT_SET}"
        assert embed_environ(text) == "value=42; none="
    finally:
        os.environ.pop("X", None)
