"""
tests.test_engine
~~~~~~~~~~~~~~~~~
Unit tests for VoxEngine.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tts_reader.engine import VoxEngine, TTSBackend


@pytest.fixture
def engine(tmp_path: Path) -> VoxEngine:
    return VoxEngine(backend=TTSBackend.GTTS, output_dir=tmp_path)


def test_speak_raises_on_empty_text(engine: VoxEngine) -> None:
    with pytest.raises(ValueError, match="empty"):
        engine.speak("")


def test_speak_raises_on_whitespace(engine: VoxEngine) -> None:
    with pytest.raises(ValueError, match="empty"):
        engine.speak("   ")


def test_speak_gtts_saves_file(tmp_path: Path) -> None:
    engine = VoxEngine(backend=TTSBackend.GTTS, output_dir=tmp_path)
    with patch("tts_reader.engine.gTTS") as mock_gtts:
        mock_instance = MagicMock()
        mock_gtts.return_value = mock_instance
        path = engine.speak("Hello from voxread", "test.mp3")
        mock_gtts.assert_called_once_with(text="Hello from voxread", lang="en", slow=False)
        mock_instance.save.assert_called_once_with(str(path))
        assert path == tmp_path / "test.mp3"


def test_speak_returns_path(tmp_path: Path) -> None:
    engine = VoxEngine(backend=TTSBackend.GTTS, output_dir=tmp_path)
    with patch("tts_reader.engine.gTTS") as mock_gtts:
        mock_gtts.return_value = MagicMock()
        path = engine.speak("Test", "out.mp3")
        assert isinstance(path, Path)
        assert path.name == "out.mp3"


def test_output_dir_created(tmp_path: Path) -> None:
    new_dir = tmp_path / "nested" / "output"
    VoxEngine(output_dir=new_dir)
    assert new_dir.exists()


def test_speak_chunks_returns_multiple_files(tmp_path: Path) -> None:
    engine = VoxEngine(backend=TTSBackend.GTTS, output_dir=tmp_path)
    long_text = "word " * 300
    with patch("tts_reader.engine.gTTS") as mock_gtts:
        mock_gtts.return_value = MagicMock()
        paths = engine.speak_chunks(long_text, chunk_size=100, base_name="chunk")
        assert len(paths) > 1


def test_speak_chunks_single_chunk_for_short_text(tmp_path: Path) -> None:
    engine = VoxEngine(backend=TTSBackend.GTTS, output_dir=tmp_path)
    with patch("tts_reader.engine.gTTS") as mock_gtts:
        mock_gtts.return_value = MagicMock()
        paths = engine.speak_chunks("Short text.", chunk_size=500)
        assert len(paths) == 1


def test_split_text_preserves_all_words() -> None:
    text = "the quick brown fox jumps over the lazy dog"
    chunks = VoxEngine._split_text(text, chunk_size=20)
    rejoined = " ".join(chunks)
    assert rejoined == text


def test_split_text_single_chunk_when_short() -> None:
    chunks = VoxEngine._split_text("short text", chunk_size=500)
    assert len(chunks) == 1
