# Railway Dockerfile for SalesBestFriend Backend
FROM python:3.11-slim

# Install ffmpeg (needed for audio conversion)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory to backend root so "app" package resolves
WORKDIR /app/backend

# Copy lightweight requirements (no torch/whisper — uses Groq API)
COPY backend/requirements-deploy.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Start uvicorn — "app.main:app" resolves from /app/backend/app/main.py
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
