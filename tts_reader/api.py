"""
voxread.api
~~~~~~~~~~~
Flask REST API for voxread.

Endpoints:
    POST /speak        — synthesise raw text
    POST /read         — synthesise an uploaded file
    GET  /health       — health check
    GET  /output/<f>   — download a generated audio file

Run locally:
    python -m tts_reader.api
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from tts_reader.engine import VoxEngine, TTSBackend
from tts_reader.reader import read_file


# ------------------------------------------------------------------
# App setup
# ------------------------------------------------------------------

app = Flask(__name__)

OUTPUT_DIR = Path("output")
UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}

OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


def _allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _unique(prefix: str, ext: str) -> str:
    """Generate a unique filename to avoid collisions."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}{ext}"


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@app.get("/health")
def health() -> tuple:
    """
    Health check endpoint.

    Returns:
        JSON with status and available backends.
    """
    return jsonify({
        "status": "ok",
        "version": "0.1.0",
        "backends": [b.value for b in TTSBackend],
    }), 200


@app.post("/speak")
def speak() -> tuple:
    """
    Synthesise raw text to speech.

    Request body (JSON):
        text     (str, required)  : text to synthesise
        backend  (str, optional)  : 'gtts' | 'pyttsx3' — default 'gtts'
        lang     (str, optional)  : language code — default 'en'

    Returns:
        JSON with the path to the generated audio file.

    Example:
        curl -X POST http://localhost:5000/speak \\
             -H "Content-Type: application/json" \\
             -d '{"text": "Hello from voxread"}'
    """
    data = request.get_json(silent=True)

    if not data or not data.get("text"):
        return jsonify({"error": "Missing required field: text"}), 400

    text: str = data["text"].strip()
    backend: str = data.get("backend", TTSBackend.GTTS.value)
    lang: str = data.get("lang", "en")

    if backend not in [b.value for b in TTSBackend]:
        return jsonify({"error": f"Invalid backend '{backend}'"}), 400

    output_file = _unique("speak", ".mp3")

    try:
        engine = VoxEngine(
            backend=TTSBackend(backend),
            lang=lang,
            output_dir=OUTPUT_DIR,
        )
        path = engine.speak(text, output_file=output_file)
        return jsonify({
            "status": "ok",
            "files": [path.name],
            "downloads": [f"/output/{path.name}"],
            "words": len(text.split()),
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/read")
def read() -> tuple:
    """
    Upload a file and synthesise its contents to speech.

    Form data:
        file     (file, required) : .txt, .pdf, or .docx
        backend  (str, optional)  : 'gtts' | 'pyttsx3' — default 'gtts'
        lang     (str, optional)  : language code — default 'en'

    Returns:
        JSON with paths to generated audio file(s).

    Example:
        curl -X POST http://localhost:5000/read \\
             -F "file=@report.pdf"
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Use field name 'file'."}), 400

    uploaded = request.files["file"]

    if not uploaded.filename or not _allowed(uploaded.filename):
        return jsonify({
            "error": f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}"
        }), 400

    backend: str = request.form.get("backend", TTSBackend.GTTS.value)
    lang: str = request.form.get("lang", "en")

    # save upload with a safe unique name
    suffix = Path(uploaded.filename).suffix.lower()
    safe_name = _unique("upload", suffix)
    upload_path = UPLOAD_DIR / secure_filename(safe_name)
    uploaded.save(upload_path)

    try:
        text = read_file(upload_path)
        word_count = len(text.split())

        engine = VoxEngine(
            backend=TTSBackend(backend),
            lang=lang,
            output_dir=OUTPUT_DIR,
        )

        base = Path(uploaded.filename).stem
        if word_count > 300:
            paths = engine.speak_chunks(text, base_name=base)
            files = [p.name for p in paths]
            downloads = [f"/output/{n}" for n in files]
        else:
            out_file = _unique(base, ".mp3")
            path = engine.speak(text, output_file=out_file)
            files = [path.name]
            downloads = [f"/output/{path.name}"]

        return jsonify({
            "status": "ok",
            "words": word_count,
            "chunks": len(files),
            "files": files,
            "downloads": downloads,
        }), 201

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # clean up the uploaded temp file
        if upload_path.exists():
            upload_path.unlink()


@app.get("/output/<filename>")
def download(filename: str) -> tuple:
    """
    Download a generated audio file.

    Args:
        filename: Name of the audio file in the output directory.

    Returns:
        The audio file as an attachment.
    """
    safe = secure_filename(filename)
    if not (OUTPUT_DIR / safe).exists():
        return jsonify({"error": "File not found."}), 404

    return send_from_directory(OUTPUT_DIR, safe, as_attachment=True)


# ------------------------------------------------------------------
# Dev server entrypoint
# ------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)