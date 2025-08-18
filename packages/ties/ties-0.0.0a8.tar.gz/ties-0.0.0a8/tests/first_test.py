"""The first test of the repository."""


def test_version_exists() -> None:
    """A test that ensures importing src succeeds and that there is a version."""
    import sys  # noqa: PLC0415

    print(sys.path)
    from ties import __version__  # noqa: PLC0415

    assert __version__ is not None
