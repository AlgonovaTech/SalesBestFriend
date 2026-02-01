"""
Transcription service with pluggable provider architecture.

Providers (priority order):
1. Gemini 2.5 Flash Lite via OpenRouter (cheap cloud, default)
2. Groq Whisper API (cloud, if GROQ_API_KEY set)
3. Modal.com diarization service (cloud, if MODAL_ENDPOINT set)
4. Local faster-whisper (dev fallback)

Usage:
    from app.services.transcription import transcribe_audio_buffer, get_provider_info

    segments = await transcribe_audio_buffer(audio_bytes, language="id")
    info = get_provider_info()  # {"provider": "gemini", "model": "...", ...}
"""

from app.services.transcription.router import (
    transcribe_audio_buffer,
    get_provider_info,
    TranscriptionProvider,
)

__all__ = [
    "transcribe_audio_buffer",
    "get_provider_info",
    "TranscriptionProvider",
]
