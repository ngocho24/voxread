"""
voxread.ai
~~~~~~~~~~
Claude-powered document Q&A. Stateless: the caller supplies the document
text and conversation history on every call. Answers are written to be
spoken aloud.
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_DOC_CHARS = 200_000
MAX_HISTORY_MESSAGES = 20

SYSTEM_PROMPT = """You are the voice assistant inside voxread, an audio reader.
Answer the user's question using only the document below. If the document
does not contain the answer, say so plainly.

Your answer will be read aloud by a text-to-speech engine, so:
- Write in natural, conversational sentences.
- Do not use markdown, bullet points, headings, tables, or emojis.
- Keep answers concise: usually two to five sentences.
- Spell out symbols and abbreviations where they would sound odd aloud.
- Reply in the same language the user asked in.

<document>
{document}
</document>"""


class AIConfigError(RuntimeError):
    """Raised when the AI backend is not configured (e.g. missing API key)."""


class DocumentChat:
    """Ask questions about a document using Claude."""

    def __init__(self, client: Any = None, model: str = DEFAULT_MODEL) -> None:
        if client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise AIConfigError(
                    "ANTHROPIC_API_KEY is not set. Add it to your .env file."
                )
            from anthropic import Anthropic

            client = Anthropic(api_key=api_key)
        self.client = client
        self.model = model

    @staticmethod
    def clean_history(history: list[dict] | None) -> list[dict]:
        """Keep only valid recent turns, starting with a user message."""
        valid = [
            {"role": m["role"], "content": str(m["content"])}
            for m in (history or [])
            if isinstance(m, dict)
            and m.get("role") in {"user", "assistant"}
            and m.get("content")
        ][-MAX_HISTORY_MESSAGES:]
        while valid and valid[0]["role"] != "user":
            valid.pop(0)
        return valid

    def ask(
        self,
        document: str,
        question: str,
        history: list[dict] | None = None,
    ) -> str:
        """Return a spoken-style answer to `question` about `document`."""
        messages = self.clean_history(history)
        messages.append({"role": "user", "content": question})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=600,
            system=SYSTEM_PROMPT.format(document=document[:MAX_DOC_CHARS]),
            messages=messages,
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()