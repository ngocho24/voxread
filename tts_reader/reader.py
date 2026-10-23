"""
voxread.reader
~~~~~~~~~~~~~~
File reader module. Extracts plain text from:
- .txt  : plain text files
- .pdf  : PDF documents via pypdf
- .docx : Word documents via python-docx

All readers return a clean string ready for the TTS engine.
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from docx import Document
from tts_reader.text import clean_text as _clean


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def read_file(path: str | Path) -> str:
    """
    Read a file and return its text content.

    Dispatches to the correct reader based on file extension.

    Args:
        path: Path to a .txt, .pdf, or .docx file.

    Returns:
        Extracted and cleaned text as a single string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError:        If the file extension is not supported.
        RuntimeError:      If the file is empty or yields no text.

    Example:
        >>> text = read_file("docs/report.pdf")
        >>> print(text[:100])
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    readers = {
        ".txt":  _read_txt,
        ".pdf":  _read_pdf,
        ".docx": _read_docx,
    }

    ext = path.suffix.lower()
    if ext not in readers:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported: {', '.join(readers)}"
        )

    text = readers[ext](path)
    text = _clean(text)

    if not text:
        raise RuntimeError(f"No readable text found in: {path}")

    return text


# ------------------------------------------------------------------
# Format-specific readers
# ------------------------------------------------------------------

def _read_txt(path: Path) -> str:
    """Read a plain text file."""
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    """Extract text from a PDF using pypdf."""
    reader = PdfReader(str(path))
    pages: list[str] = []

    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)
        else:
            # warn but don't fail — scanned pages return nothing
            print(f"  [voxread] page {i + 1} yielded no text (possibly scanned).")

    return "\n".join(pages)


def _read_docx(path: Path) -> str:
    """Extract text from a Word document."""
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
