"""Test configuration loading, using the pyproject.toml."""

from ties._configuration import load_config


def test_load_config() -> None:
    """Test that the config is loaded without an error."""
    config = load_config()
    assert "tie" in config
    assert len(config["tie"]) == 5
