"""
voxread.cli
~~~~~~~~~~~
Command-line interface for voxread.

Usage examples:
    voxread speak "Hello from voxread"
    voxread read report.pdf
    voxread read report.pdf --backend pyttsx3 --lang en --output my_audio.mp3
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from tts_reader.engine import VoxEngine, TTSBackend
from tts_reader.reader import read_file


# ------------------------------------------------------------------
# CLI group
# ------------------------------------------------------------------

@click.group()
@click.version_option(version="0.1.0", prog_name="voxread")
def cli() -> None:
    """
    voxread — a text-to-speech audio reader.

    Convert text or documents to spoken audio files.
    """


# ------------------------------------------------------------------
# speak command — raw text input
# ------------------------------------------------------------------

@cli.command()
@click.argument("text")
@click.option(
    "--backend", "-b",
    type=click.Choice([b.value for b in TTSBackend], case_sensitive=False),
    default=TTSBackend.GTTS.value,
    show_default=True,
    help="TTS backend: gtts (online) or pyttsx3 (offline).",
)
@click.option(
    "--lang", "-l",
    default="en",
    show_default=True,
    help="Language code for gTTS (e.g. en, fr, sw).",
)
@click.option(
    "--output", "-o",
    default="output.mp3",
    show_default=True,
    help="Output audio filename.",
)
@click.option(
    "--output-dir", "-d",
    default="output",
    show_default=True,
    help="Directory to save audio files.",
)
def speak(
    text: str,
    backend: str,
    lang: str,
    output: str,
    output_dir: str,
) -> None:
    """
    Convert TEXT directly to speech.

    \b
    Example:
        voxread speak "Good morning, Elijah"
        voxread speak "Habari yako" --lang sw
    """
    engine = VoxEngine(
        backend=TTSBackend(backend),
        lang=lang,
        output_dir=output_dir,
    )

    click.echo(f"  backend : {backend}")
    click.echo(f"  lang    : {lang}")
    click.echo(f"  output  : {output_dir}/{output}")
    click.echo("")

    try:
        path = engine.speak(text, output_file=output)
        click.secho(f"✓ Saved: {path}", fg="green")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


# ------------------------------------------------------------------
# read command — file input
# ------------------------------------------------------------------

@cli.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--backend", "-b",
    type=click.Choice([b.value for b in TTSBackend], case_sensitive=False),
    default=TTSBackend.GTTS.value,
    show_default=True,
    help="TTS backend: gtts (online) or pyttsx3 (offline).",
)
@click.option(
    "--lang", "-l",
    default="en",
    show_default=True,
    help="Language code for gTTS (e.g. en, fr, sw).",
)
@click.option(
    "--output", "-o",
    default=None,
    help="Output filename. Defaults to <input_file>.mp3.",
)
@click.option(
    "--output-dir", "-d",
    default="output",
    show_default=True,
    help="Directory to save audio files.",
)
@click.option(
    "--chunk-size", "-c",
    default=500,
    show_default=True,
    help="Max characters per audio chunk for long documents.",
)
def read(
    file: str,
    backend: str,
    lang: str,
    output: str | None,
    output_dir: str,
    chunk_size: int,
) -> None:
    """
    Read a FILE and convert its contents to speech.

    Supports .txt, .pdf, and .docx formats.

    \b
    Example:
        voxread read report.pdf
        voxread read notes.txt --output notes.mp3
        voxread read thesis.docx --backend pyttsx3 --chunk-size 300
    """
    input_path = Path(file)
    output_file = output or f"{input_path.stem}.mp3"

    click.echo(f"  file    : {file}")
    click.echo(f"  backend : {backend}")
    click.echo(f"  lang    : {lang}")
    click.echo(f"  output  : {output_dir}/{output_file}")
    click.echo("")

    # extract text
    try:
        click.echo("→ Extracting text...")
        text = read_file(input_path)
        word_count = len(text.split())
        click.echo(f"  {word_count} words extracted.")
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        click.secho(f"✗ {e}", fg="red", err=True)
        sys.exit(1)

    # synthesise
    engine = VoxEngine(
        backend=TTSBackend(backend),
        lang=lang,
        output_dir=output_dir,
    )

    try:
        click.echo("→ Synthesising audio...")
        if word_count > 300:
            # long document — chunk it
            paths = engine.speak_chunks(
                text,
                chunk_size=chunk_size,
                base_name=input_path.stem,
            )
            click.secho(
                f"✓ {len(paths)} audio chunks saved to {output_dir}/",
                fg="green",
            )
        else:
            path = engine.speak(text, output_file=output_file)
            click.secho(f"✓ Saved: {path}", fg="green")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)