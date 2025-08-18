"""Tests of the common transforms."""

import os

from ties.common_transforms import embed_environ


def test_embed_environ() -> None:
    """Test the embed_environ transform."""
    env_var_name = "TEMP_VAR"
    os.environ[env_var_name] = "tie"

    assert embed_environ("How's my ${env:TEMP_VAR}?") == "How's my tie?"
