# voxread — Python TTS engine
FROM python:3.11-slim

WORKDIR /app

# system deps for pyttsx3 (offline backend)
RUN apt-get update && apt-get install -y \
    espeak \
    espeak-ng \
    libespeak-ng1 \
    && rm -rf /var/lib/apt/lists/*

# install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# copy source
COPY tts_reader/ ./tts_reader/

# output dir
RUN mkdir -p output uploads

EXPOSE 5000

CMD ["python", "-m", "tts_reader.api"]
