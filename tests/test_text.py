import pytest

from tts_reader.engine import TTSBackend, VoxEngine
from tts_reader.text import clean_text


def test_clean_text_is_idempotent():
    messy = "\u201CHi\u201D \u2014 there\n\n\n\nbye  "
    once = clean_text(messy)
    assert clean_text(once) == once


@pytest.fixture
def engine(tmp_path, monkeypatch):
    seen = {}

    def fake_gtts(self, text, path):
        seen["text"] = text
        return path

    monkeypatch.setattr(VoxEngine, "_speak_gtts", fake_gtts)
    eng = VoxEngine(backend=TTSBackend.GTTS, lang="en", output_dir=tmp_path)
    return eng, seen


def test_speak_cleans_raw_text(engine):
    eng, seen = engine
    eng.speak("\u201CHi\u201D \u2014 there")
    assert seen["text"] == '"Hi" - there'


def test_speak_rejects_text_that_cleans_to_nothing(engine):
    eng, _ = engine
    with pytest.raises(ValueError):
        eng.speak("   \x00\x01  ")