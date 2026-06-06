# voxread

> A text-to-speech audio reader with a Python backend and React/TypeScript frontend.

Built by [Elijah Ngocho Kamau](https://github.com/ngocho24) — Nyeri, Kenya.

---

## Overview

voxread converts text and documents to spoken audio. It supports two TTS backends — Google TTS (online) and pyttsx3 (offline) — and accepts `.txt`, `.pdf`, and `.docx` files.

## Stack

| Layer | Tech |
|---|---|
| TTS engine | Python, gTTS, pyttsx3 |
| File reader | PyPDF2, python-docx |
| CLI | Click |
| REST API | Flask, flask-cors |
| Frontend | React, TypeScript, Vite |
| Container | Docker, docker-compose |
| Tests | pytest (18 passing) |

## Project Structure
voxread/
├── tts_reader/
│   ├── init.py      # package exports
│   ├── engine.py        # VoxEngine — gTTS + pyttsx3 backends
│   ├── reader.py        # file reader — .txt .pdf .docx
│   ├── cli.py           # Click CLI — speak + read commands
│   └── api.py           # Flask REST API
├── src/cli/
│   └── index.ts         # TypeScript CLI wrapper
├── frontend/            # React + TypeScript UI
├── tests/               # pytest unit tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml

## Installation

### Requirements
- Python 3.11+
- Node.js 20+
- WSL (Ubuntu) or Linux

### Backend setup

```bash
git clone git@github.com:ngocho24/voxread.git
cd voxread
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### Frontend setup

```bash
cd frontend
npm install
```

## Usage

### Python CLI

```bash
# activate venv first
source .venv/bin/activate

# speak raw text
voxread speak "Hello from voxread"

# speak in Swahili
voxread speak "Habari yako. Karibu voxread." --lang sw

# read a file (offline)
voxread read report.pdf --backend pyttsx3

# read a docx
voxread read notes.docx --output notes.mp3
```

### REST API

Start the server:
```bash
python -m tts_reader.api
```

Endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/speak` | Synthesise raw text |
| POST | `/read` | Upload and synthesise a file |
| GET | `/output/<file>` | Download generated audio |

Examples:

```bash
# health check
curl http://localhost:5000/health

# speak text
curl -X POST http://localhost:5000/speak \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello from voxread", "lang": "en"}'

# upload a file
curl -X POST http://localhost:5000/read \
     -F "file=@report.pdf" \
     -F "lang=en"
```

### TypeScript CLI

```bash
cd src/cli
npx tsx index.ts health
npx tsx index.ts speak "Hello from TypeScript"
npx tsx index.ts read ../../report.pdf
```

### Frontend

```bash
# Terminal 1 — start the API
source .venv/bin/activate
python -m tts_reader.api

# Terminal 2 — start the frontend
cd frontend
npm run dev
```

Open `http://localhost:5173`.

### Docker

```bash
docker-compose up --build
```

API available at `http://localhost:5000`.

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

Expected: **18 passed**.

## Supported Languages (gTTS)

| Code | Language |
|---|---|
| `en` | English |
| `sw` | Swahili |
| `fr` | French |
| `de` | German |
| `es` | Spanish |
| `ar` | Arabic |

## Author

**Elijah Ngocho Kamau**
- GitHub: [github.com/ngocho24](https://github.com/ngocho24)
- LinkedIn: [linkedin.com/in/elijah-ngocho](https://www.linkedin.com/in/elijah-ngocho-85347b160/)
- Email: elijahngocho24@gmail.com