"""
voxread.text
~~~~~~~~~~~~
Text normalisation shared by every input path: files, CLI, API and AI answers.
"""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """
    Normalise text for TTS consumption.

    - Collapse multiple blank lines into one
    - Strip leading/trailing whitespace per line
    - Remove non-printable characters
    - Normalise unicode dashes and quotes

    Idempotent: cleaning already-clean text returns it unchanged.
    """
    # remove non-printable characters (keeps newlines, tabs)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", " ", text)

    # normalise unicode punctuation to ASCII equivalents
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201C", '"').replace("\u201D", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")

    # strip each line and collapse excessive blank lines
    lines = [line.strip() for line in text.splitlines()]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))

    return text.strip()