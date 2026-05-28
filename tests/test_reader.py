"""
tests.test_reader
~~~~~~~~~~~~~~~~~
Unit tests for the file reader module.
"""

from pathlib import Path

import pytest

from tts_reader.reader import read_file, _clean


def test_read_txt_returns_content(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("Hello from voxread.", encoding="utf-8")
    assert read_file(f) == "Hello from voxread."


def test_read_txt_strips_whitespace(tmp_path: Path) -> None:
    f = tmp_path / "sample.txt"
    f.write_text("  hello world  \n\n\n  ", encoding="utf-8")
    assert read_file(f) == "hello world"


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


def test_clean_normalises_unicode_quotes() -> None:
    assert _clean("\u201CHello\u201D") == '"Hello"'


def test_clean_normalises_unicode_dashes() -> None:
    assert _clean("well\u2014known") == "well-known"


def test_clean_collapses_blank_lines() -> None:
    assert "\n\n\n" not in _clean("line1\n\n\n\n\nline2")


def test_clean_strips_non_printable() -> None:
    assert "\x00" not in _clean("hello\x00world")
