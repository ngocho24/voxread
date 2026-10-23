import io
from pathlib import Path

import pytest

from tts_reader import api
from tts_reader.ai import MAX_DOC_CHARS, AIConfigError


class FakeChat:
    def __init__(self):
        self.calls = []

    def ask(self, document, question, history=None):
        self.calls.append((document, question, history))
        return "The answer is forty two."


class FakeEngine:
    def __init__(self, **kwargs):
        pass

    def speak(self, text, output_file=None):
        return Path(output_file)


@pytest.fixture
def client(monkeypatch):
    fake = FakeChat()
    monkeypatch.setattr(api, "get_chat", lambda: fake)
    monkeypatch.setattr(api, "VoxEngine", FakeEngine)
    api.app.config["TESTING"] = True
    return api.app.test_client(), fake


def _upload(c, text="Paris is the capital of France.", name="notes.txt"):
    return c.post(
        "/documents",
        data={"file": (io.BytesIO(text.encode()), name)},
        content_type="multipart/form-data",
    )


def test_documents_returns_text(client):
    c, _ = client
    r = _upload(c)
    assert r.status_code == 200
    body = r.get_json()
    assert "Paris" in body["text"]
    assert body["words"] == 6
    assert body["truncated"] is False


def test_documents_rejects_bad_extension(client):
    c, _ = client
    assert _upload(c, name="virus.exe").status_code == 400


def test_chat_returns_answer_and_audio(client):
    c, fake = client
    r = c.post("/chat", json={"document": "Some text.", "question": "What?"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["answer"] == "The answer is forty two."
    assert body["audio"].startswith("/output/answer_")
    assert fake.calls[0][0] == "Some text."
    assert fake.calls[0][1] == "What?"


def test_chat_without_audio(client):
    c, _ = client
    r = c.post(
        "/chat", json={"document": "Text.", "question": "Hi", "speak": False}
    )
    assert r.get_json()["audio"] is None


def test_chat_missing_fields(client):
    c, _ = client
    assert c.post("/chat", json={"question": "Hi"}).status_code == 400


def test_chat_document_too_large(client):
    c, _ = client
    big = "x" * (MAX_DOC_CHARS + 1)
    r = c.post("/chat", json={"document": big, "question": "Hi"})
    assert r.status_code == 413


def test_chat_ai_not_configured(client, monkeypatch):
    c, _ = client

    def boom():
        raise AIConfigError("no key")

    monkeypatch.setattr(api, "get_chat", boom)
    r = c.post("/chat", json={"document": "Text.", "question": "Hi"})
    assert r.status_code == 503


def test_health_reports_ai_configured(client, monkeypatch):
    c, _ = client
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    assert c.get("/health").get_json()["ai_configured"] is True

    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert c.get("/health").get_json()["ai_configured"] is False
