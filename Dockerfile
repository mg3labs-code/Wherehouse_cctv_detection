# Railway / cloud: CPU-only (no NVIDIA GPU). Local GPU builds can still use docker-compose.
FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8001

# OpenCV / Ultralytics system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# CPU PyTorch first (much smaller than CUDA wheels)
RUN pip install --upgrade pip \
    && pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
# Prefer headless OpenCV in containers; drop torch lines already installed
RUN grep -vE '^(torch|torchvision|torchaudio|opencv-python)' requirements.txt > /tmp/req.txt \
    && pip install -r /tmp/req.txt \
    && pip install opencv-python-headless

COPY . .

RUN mkdir -p data/dataset data/videos outputs/logs outputs/reports outputs/videos models \
    && ln -sf /usr/local/bin/python /usr/local/bin/python3 || true

# Optional frontend build (skip if Node not needed / dist already present)
# Railway serves API; React dist is mounted by FastAPI when frontend/dist exists.

EXPOSE 8001

# Railway injects $PORT — bind API there
CMD ["sh", "-c", "uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8001}"]
