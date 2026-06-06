# voxread — frontend

> React + TypeScript UI for the voxread text-to-speech engine.

Part of the [voxread](https://github.com/ngocho24/voxread) project.

---

## Stack

- **React 18** + **TypeScript**
- **Vite** — dev server and bundler
- **CSS variables** — design system
- Google Fonts — Syne + DM Mono

## Getting Started

### Requirements
- Node.js 20+
- voxread backend running on `http://localhost:5000`

### Install and run

```bash
# from the project root
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### Start the backend first

```bash
# from project root
source ../.venv/bin/activate
python -m tts_reader.api
```

## Features

- **Text mode** — type or paste text, click speak
- **File mode** — drag and drop `.txt`, `.pdf`, or `.docx`
- **Backend selector** — gtts (online) or pyttsx3 (offline)
- **Language selector** — English, Swahili, French, German, Spanish, Arabic
- **Inline audio player** — play and download generated audio
- **Multi-chunk support** — long documents split into parts

## Project Structure
frontend/
├── src/
│   ├── api/
│   │   └── voxread.ts        # typed API client
│   ├── components/
│   │   ├── AudioPlayer.tsx   # audio playback + download
│   │   └── Controls.tsx      # backend + language selectors
│   ├── App.tsx               # main app — text + file modes
│   ├── main.tsx              # entry point
│   └── index.css             # design system + global styles
├── public/
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts

## API Integration

The frontend talks to the Flask backend at `http://localhost:5000`.

| Action | Endpoint |
|---|---|
| Speak text | `POST /speak` |
| Read file | `POST /read` |
| Download audio | `GET /output/<file>` |
| Health check | `GET /health` |

The typed API client lives in `src/api/voxread.ts`.

## Build for Production

```bash
npm run build
```

Output goes to `frontend/dist/`. Serve it behind nginx or any static host.

## Author

**Elijah Ngocho Kamau** — [github.com/ngocho24](https://github.com/ngocho24)