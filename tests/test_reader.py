"""
tests.test_reader
~~~~~~~~~~~~~~~~~
Unit tests for the file reader module.

Run with:
    pytest tests/ -v
"""

from pathlib import Path

import pytest

from tts_reader.reader import read_file, _clean


# ------------------------------------------------------------------
# read_file() — .txt
# ------------------------------------------------------------------

def test_read_txt_returns_content(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("Hello from voxread.", encoding="utf-8")
    assert read_file(f) == "Hello from voxread."


def test_read_txt_strips_whitespace(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("  hello world  \n\n\n  ", encoding="utf-8")
    result = read_file(f)
    assert result == "hello world"


def test_read_file_raises_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        read_file("/nonexistent/file.txt")


def test_read_file_raises_for_unsupported_extension(tmp_path: Path) -> None:
    f = tmp_path / "file.xyz"
    f.write_text("content")
    with pytest.raises(ValueError, match="Unsupported"):
        read_file(f)


def test_read_file_raises_for_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("   \n\n   ", encoding="utf-8")
    with pytest.raises(RuntimeError, match="No readable text"):
        read_file(f)


# ------------------------------------------------------------------
# _clean()
# ------------------------------------------------------------------

def test_clean_normalises_unicode_quotes() -> None:
    result = _clean("\u201CHello\u201D")
    assert result == '"Hello"'


def test_clean_normalises_unicode_dashes() -> None:
    result = _clean("well\u2014known")
    assert result == "well-known"


def test_clean_collapses_blank_lines() -> None:
    result = _clean("line1\n\n\n\n\nline2")
    assert "\n\n\n" not in result


def test_clean_strips_non_printable() -> None:
    result = _clean("hello\x00world")
    assert "\x00" not in result