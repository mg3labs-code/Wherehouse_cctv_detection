FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

WORKDIR /app

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create directories
RUN mkdir -p data/dataset outputs/{logs,reports,videos}

# Default command
CMD ["python", "-m", "src.main", "monitor", "--source", "rtsp://camera/stream"]
