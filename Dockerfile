# Railway Dockerfile for SalesBestFriend Backend
# CACHE BREAK: 2025-11-19 22:24 - Force rebuild to install python-multipart
FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/backend

# Copy requirements first (for better Docker layer caching)
COPY backend/requirements.txt .

# Install Python dependencies (including python-multipart)
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Start uvicorn (already in /app/backend)
CMD uvicorn main_trial_class:app --host 0.0.0.0 --port ${PORT:-8000}

