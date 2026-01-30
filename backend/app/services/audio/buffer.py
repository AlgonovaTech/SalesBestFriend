"""
Audio buffer for real-time transcription.
Accumulates audio chunks and triggers transcription periodically.

Ported from utils/audio_buffer.py.
"""

import io
import time
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


class AudioBuffer:
    """Manages audio chunks for periodic transcription."""

    def __init__(self, interval_seconds: float = 10.0):
        self.interval_seconds = interval_seconds
        self.buffer = io.BytesIO()
        self.last_transcription_time = time.time()
        self.chunk_count = 0
        self.min_chunks = 8
        self.min_buffer_size = 60_000  # 60KB minimum

    def add_chunk(self, chunk: bytes) -> bool:
        """Add audio chunk. Returns True if ready for transcription."""
        self.buffer.write(chunk)
        self.chunk_count += 1

        elapsed = time.time() - self.last_transcription_time
        buffer_size = self.buffer.tell()

        if (
            elapsed >= self.interval_seconds
            and self.chunk_count >= self.min_chunks
            and buffer_size >= self.min_buffer_size
        ):
            logger.info(
                "Buffer ready: %d chunks, %d bytes, %.1fs elapsed",
                self.chunk_count, buffer_size, elapsed,
            )
            return True

        return False

    def get_audio_data(self) -> bytes:
        return self.buffer.getvalue()

    def clear(self):
        self.buffer = io.BytesIO()
        self.last_transcription_time = time.time()
        self.chunk_count = 0

    def save_to_temp_file(self, suffix: str = ".webm") -> str:
        data = self.get_audio_data()
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return temp_path

    def has_data(self) -> bool:
        return self.chunk_count > 0
