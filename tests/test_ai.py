from types import SimpleNamespace

import pytest

from tts_reader.ai import AIConfigError, DocumentChat


class FakeAnthropic:
    def __init__(self):
        self.kwargs = None
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=" Hello. ")]
        )


def test_ask_builds_request_and_strips_output():
    fake = FakeAnthropic()
    history = [
        {"role": "assistant", "content": "orphan reply"},  # must be dropped
        {"role": "user", "content": "first q"},
        {"role": "assistant", "content": "first a"},
    ]
    out = DocumentChat(client=fake).ask("DOC {with braces}", "second q", history)

    assert out == "Hello."
    assert "DOC {with braces}" in fake.kwargs["system"]
    msgs = fake.kwargs["messages"]
    assert msgs[0] == {"role": "user", "content": "first q"}
    assert msgs[-1] == {"role": "user", "content": "second q"}
    assert len(msgs) == 3


def test_clean_history_ignores_garbage():
    cleaned = DocumentChat.clean_history(
        [None, {"role": "system", "content": "x"}, {"role": "user", "content": ""}]
    )
    assert cleaned == []


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(AIConfigError):
        DocumentChat()