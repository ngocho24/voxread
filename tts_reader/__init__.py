"""
voxread
~~~~~~~
A text-to-speech audio reader.

Basic usage:
    >>> from tts_reader.engine import VoxEngine
    >>> engine = VoxEngine()
    >>> path = engine.speak("Hello from voxread", "hello.mp3")

CLI usage:
    voxread speak "Hello from voxread"
    voxread read report.pdf

API usage:
    python -m tts_reader.api
"""

from tts_reader.engine import VoxEngine, TTSBackend
from tts_reader.reader import read_file

__version__ = "0.1.0"
__author__ = "Elijah Ngocho Kamau"
__all__ = ["VoxEngine", "TTSBackend", "read_file"]
