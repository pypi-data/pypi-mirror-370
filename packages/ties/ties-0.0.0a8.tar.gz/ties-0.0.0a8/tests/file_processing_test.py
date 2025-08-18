"""Tests for `ties._file_processing` covering core branches."""

from __future__ import annotations

from pathlib import Path

import pytest

from ties._file_processing import (
    final_summary,
    get_content_hash,
    get_file_hash,
    get_source_content,
    is_text_file,
    normalize_targets,
    process_files,
)


def write(path: Path, content: str) -> None:
    """Create parent directories and write UTF-8 text to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_get_content_hash_and_file_hash(tmp_path: Path) -> None:
    """Hashing a byte string and a file should be consistent; missing file is ''."""
    content = b"abc"
    assert get_content_hash(content) == get_content_hash(content)

    file_path = tmp_path / "x.txt"
    file_path.write_bytes(content)
    assert get_file_hash(file_path) == get_content_hash(content)

    # Missing file returns empty string
    assert get_file_hash(tmp_path / "missing.txt") == ""


def test_is_text_file_true_and_false(tmp_path: Path) -> None:
    """`is_text_file` returns True for UTF-8 text and False for invalid UTF-8."""
    text_path = tmp_path / "a.txt"
    write(text_path, "hello")
    assert is_text_file(text_path) is True

    # Invalid UTF-8 should be considered non-text
    bin_path = tmp_path / "b.bin"
    bin_path.write_bytes(b"\xff\xfe\x00\x00")
    assert is_text_file(bin_path) is False


def test_resolve_sources_and_transforms_branches(tmp_path: Path) -> None:
    """Cover single source, concatenation, and concat error with binary input."""
    src = tmp_path / "s.txt"
    write(src, "one")

    # Single source
    assert get_source_content({"source": str(src)}, tmp_path).decode("utf-8") == "one"

    # Concatenate two sources with newline between
    src2 = tmp_path / "s2.txt"
    write(src2, "two")
    out = get_source_content({"sources": [str(src), str(src2)]}, tmp_path).decode(
        "utf-8"
    )
    assert out == "one\ntwo"

    # Concatenation with non-text should raise
    bin_path = tmp_path / "b.bin"
    bin_path.write_bytes(b"\xff\xfe\x00\x00")
    with pytest.raises(TypeError):
        get_source_content({"sources": [str(src), str(bin_path)]}, tmp_path)


def test_transform_success(tmp_path: Path) -> None:
    """A custom transform module is imported and applied successfully."""
    # Create a simple transform module in a dedicated script dir
    script_dir = Path("tests/data/scripts")

    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    write(a, "A")
    write(b, "B")

    config = {
        "sources": [str(a), str(b)],
        "transform": "mymods:join_with_dash",
    }
    result = get_source_content(config, script_dir).decode("utf-8")
    assert result == "A-B"


def test_transform_errors(tmp_path: Path) -> None:
    """Bad transform spec or missing module raises a RuntimeError."""
    a = tmp_path / "a.txt"
    write(a, "A")

    # Bad spec (no colon)
    with pytest.raises(RuntimeError):
        get_source_content({"source": str(a), "transform": "badformat"}, tmp_path)

    # Non-existent module
    with pytest.raises(RuntimeError):
        get_source_content(
            {"source": str(a), "transform": "no_such_mod:func"}, tmp_path
        )


def test_process_files_check_and_fix(tmp_path: Path) -> None:
    """When out of sync, check is False; fix writes and returns True."""
    src = tmp_path / "source.txt"
    dst = tmp_path / "dest.txt"
    write(src, "hello")
    write(dst, "world")

    cfg = {"tie": [{"source": str(src), "target": str(dst)}]}
    assert process_files(cfg, mode="check") is False

    # Fix should write and return True
    assert process_files(cfg, mode="fix") is True
    assert dst.read_text(encoding="utf-8") == "hello"


def test_process_files_fix_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Write errors are reported and cause fix mode to return False."""
    src = tmp_path / "source.txt"
    dst = tmp_path / "dest.txt"
    write(src, "hello")
    write(dst, "world")

    # Force write error

    def boom(_self: Path, _data: bytes) -> int:  # type: ignore[override]
        raise OSError("boom")

    monkeypatch.setattr(Path, "write_bytes", boom, raising=True)
    cfg = {"tie": [{"source": str(src), "target": str(dst)}]}
    assert process_files(cfg, mode="fix") is False
    # restore happens automatically via monkeypatch


def test_process_files_fix_already_in_sync(tmp_path: Path) -> None:
    """Fix mode returns True and makes no changes when already in sync."""
    src = tmp_path / "source.txt"
    dst = tmp_path / "dest.txt"
    write(src, "hello")
    write(dst, "hello")

    cfg = {"tie": [{"source": str(src), "target": str(dst)}]}
    assert process_files(cfg, mode="fix") is True


def test_normalize_targets_missing_raises() -> None:
    """Missing target(s) key causes a ValueError."""
    with pytest.raises(ValueError):
        normalize_targets({})


def test_final_summary_variants() -> None:
    """Cover both modes of `final_summary` across success and failure cases."""
    # check mode with discrepancies
    assert final_summary("check", discrepancies=1, fixed_count=0, errors=0) is False
    # check mode with none
    assert final_summary("check", discrepancies=0, fixed_count=0, errors=0) is True

    # fix mode: with fixes and no errors
    assert final_summary("fix", discrepancies=0, fixed_count=2, errors=0) is True
    # fix mode: with errors
    assert final_summary("fix", discrepancies=0, fixed_count=0, errors=1) is False
    # fix mode: nothing to do
    assert final_summary("fix", discrepancies=0, fixed_count=0, errors=0) is True
