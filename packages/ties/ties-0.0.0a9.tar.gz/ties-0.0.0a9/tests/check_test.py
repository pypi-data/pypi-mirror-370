"""Tests of the check mode."""

from ties import process_files


def test_check_equal_target() -> None:
    """Test that equal target check is valid."""
    assert process_files(
        {
            "tie": [
                {
                    "source": "tests/data/A1.txt",
                    "target": "tests/data/A2.txt",
                }
            ]
        },
        mode="check",
    )


def test_check_non_equal_target() -> None:
    """Test that non equal target check is invalid."""
    assert not process_files(
        {
            "tie": [
                {
                    "source": "tests/data/A1.txt",
                    "target": "tests/data/B.txt",
                }
            ]
        },
        mode="check",
    )


def test_check_one_equal_one_non_targets() -> None:
    """Test that one equal one non targets check is invalid."""
    assert not process_files(
        {
            "tie": [
                {
                    "source": "tests/data/A1.txt",
                    "targets": ["tests/data/A2.txt", "tests/data/B.txt"],
                }
            ]
        },
        mode="check",
    )
