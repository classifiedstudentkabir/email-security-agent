# =============================================================================
# Local AI Email Security Agent — Dockerfile
# =============================================================================
# Build:   docker compose build
# Run:     docker compose up
# =============================================================================

# Use the official Python 3.13 slim image for a small, production-ready base
FROM python:3.13-slim

# --------------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------------
LABEL maintainer="Local AI Email Security Agent"
LABEL description="Privacy-first email security pipeline powered by local Ollama AI"
LABEL version="1.0"

# --------------------------------------------------------------------------
# Environment defaults
# --------------------------------------------------------------------------
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr (ensures logs appear immediately)
ENV PYTHONUNBUFFERED=1
# Default Ollama URL for Docker — host.docker.internal reaches the host machine
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
# Default model — override in .env or docker-compose.yml
ENV OLLAMA_MODEL=qwen2.5:1.5b

# --------------------------------------------------------------------------
# System dependencies
# --------------------------------------------------------------------------
# We only need a minimal set; httpx and other pure-Python deps need no extras
RUN apt-get update && apt-get install -y --no-install-recommends \
    # ca-certificates is required for HTTPS/IMAP SSL connections
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# Working directory
# --------------------------------------------------------------------------
WORKDIR /app

# --------------------------------------------------------------------------
# Install Python dependencies first (leverages Docker layer caching)
# Copy requirements before source so this layer only rebuilds on dep changes
# --------------------------------------------------------------------------
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------------------------
# Copy source code
# --------------------------------------------------------------------------
COPY main.py ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# --------------------------------------------------------------------------
# Create logs directory (mounted as a volume in docker-compose.yml)
# --------------------------------------------------------------------------
RUN mkdir -p /app/logs

# --------------------------------------------------------------------------
# Run the agent in scan + watch mode by default
# Override CMD in docker-compose.yml or at runtime for other modes:
#   --scan          one-shot scan
#   --scan --watch  continuous watch (default)
#   --test          test against fixture emails (no IMAP needed)
#   --check         health-check Ollama connection
# --------------------------------------------------------------------------
CMD ["python", "main.py", "--scan", "--watch"]
