"""
voxread.engine
~~~~~~~~~~~~~~
Core TTS engine. Supports two backends:
- gTTS  : online, uses Google Text-to-Speech API (better quality)
- pyttsx3: offline, uses system voices (no internet needed)
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path

from gtts import gTTS
import pyttsx3


class TTSBackend(str, Enum):
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"


class VoxEngine:
    """
    Text-to-speech engine for voxread.

    Args:
        backend: Which TTS backend to use. Defaults to gTTS.
        lang: Language code for gTTS (e.g. 'en', 'fr'). Ignored by pyttsx3.
        rate: Speech rate for pyttsx3 (words per minute). Ignored by gTTS.
        output_dir: Directory where audio files are saved.

    Example:
        >>> engine = VoxEngine(backend=TTSBackend.GTTS)
        >>> path = engine.speak("Hello from voxread", output_file="hello.mp3")
    """

    def __init__(
        self,
        backend: TTSBackend = TTSBackend.GTTS,
        lang: str = "en",
        rate: int = 150,
        output_dir: str | Path = "output",
    ) -> None:
        self.backend = backend
        self.lang = lang
        self.rate = rate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # initialise pyttsx3 engine once (expensive to recreate)
        self._pyttsx3_engine: pyttsx3.Engine | None = None
        if self.backend == TTSBackend.PYTTSX3:
            self._pyttsx3_engine = pyttsx3.init()
            self._pyttsx3_engine.setProperty("rate", self.rate)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def speak(self, text: str, output_file: str = "output.mp3") -> Path:
        """
        Convert text to speech and save to a file.

        Args:
            text: The text to convert.
            output_file: Filename for the audio output.

        Returns:
            Path to the saved audio file.

        Raises:
            ValueError: If text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Cannot synthesise empty text.")

        output_path = self.output_dir / output_file

        if self.backend == TTSBackend.GTTS:
            return self._speak_gtts(text, output_path)

        return self._speak_pyttsx3(text, output_path)

    def speak_chunks(
        self, text: str, chunk_size: int = 500, base_name: str = "chunk"
    ) -> list[Path]:
        """
        Split long text into chunks and synthesise each one.
        Useful for long documents where gTTS has request size limits.

        Args:
            text: Full text to synthesise.
            chunk_size: Max characters per chunk.
            base_name: Base filename prefix for each chunk.

        Returns:
            List of paths to generated audio files.
        """
        chunks = self._split_text(text, chunk_size)
        paths: list[Path] = []

        for i, chunk in enumerate(chunks):
            filename = f"{base_name}_{i:03d}.mp3"
            path = self.speak(chunk, output_file=filename)
            paths.append(path)

        return paths

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _speak_gtts(self, text: str, output_path: Path) -> Path:
        tts = gTTS(text=text, lang=self.lang, slow=False)
        tts.save(str(output_path))
        return output_path

    def _speak_pyttsx3(self, text: str, output_path: Path) -> Path:
        assert self._pyttsx3_engine is not None
        self._pyttsx3_engine.save_to_file(text, str(output_path))
        self._pyttsx3_engine.runAndWait()
        return output_path

    @staticmethod
    def _split_text(text: str, chunk_size: int) -> list[str]:
        """Split text on sentence boundaries where possible."""
        words = text.split()
        chunks, current = [], []
        length = 0

        for word in words:
            if length + len(word) + 1 > chunk_size and current:
                chunks.append(" ".join(current))
                current, length = [], 0
            current.append(word)
            length += len(word) + 1

        if current:
            chunks.append(" ".join(current))

        return chunks