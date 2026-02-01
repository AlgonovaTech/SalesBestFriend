"""
Transcription router — selects and manages providers.

Provider selection priority:
1. Explicit TRANSCRIPTION_BACKEND env var
2. Modal (if MODAL_TRANSCRIPTION_ENDPOINT is set)
3. Gemini (default, uses OPENROUTER_API_KEY)
4. Groq (if GROQ_API_KEY is set)
5. Local (dev fallback, if faster-whisper installed)

Usage:
    segments = await transcribe_audio_buffer(audio_bytes, language="id")
"""

import logging
import os
from typing import Dict, List, Optional

from app.services.transcription.base import TranscriptionProvider, TranscriptSegment

logger = logging.getLogger(__name__)

# Lazy-loaded provider instances
_providers: Dict[str, TranscriptionProvider] = {}


def _get_provider(name: str) -> TranscriptionProvider:
    """Get or create a provider instance by name."""
    if name not in _providers:
        if name == "gemini":
            from app.services.transcription.gemini_provider import GeminiTranscriptionProvider
            _providers[name] = GeminiTranscriptionProvider()
        elif name == "groq":
            from app.services.transcription.groq_provider import GroqTranscriptionProvider
            _providers[name] = GroqTranscriptionProvider()
        elif name == "modal":
            from app.services.transcription.modal_provider import ModalTranscriptionProvider
            _providers[name] = ModalTranscriptionProvider()
        elif name == "local":
            from app.services.transcription.local_provider import LocalTranscriptionProvider
            _providers[name] = LocalTranscriptionProvider()
        else:
            raise ValueError(f"Unknown transcription provider: {name}")
    return _providers[name]


def _select_provider() -> str:
    """
    Select the best available transcription provider.

    Priority:
    1. TRANSCRIPTION_BACKEND env var (explicit override)
    2. modal (if endpoint configured — best quality + diarization)
    3. gemini (default — cheap and always available)
    4. groq (if API key set)
    5. local (if faster-whisper installed)
    """
    # Check explicit config
    try:
        from app.config import get_settings
        settings = get_settings()
        explicit = settings.transcription_backend or os.environ.get("TRANSCRIPTION_BACKEND", "")
    except Exception:
        explicit = os.environ.get("TRANSCRIPTION_BACKEND", "")
    explicit = explicit.lower()

    if explicit:
        provider = _get_provider(explicit)
        if provider.is_available():
            return explicit
        logger.warning(
            "Requested provider '%s' is not available, falling back",
            explicit,
        )

    # Auto-select by priority
    modal = _get_provider("modal")
    if modal.is_available():
        return "modal"

    # Default: Gemini via OpenRouter
    gemini = _get_provider("gemini")
    if gemini.is_available():
        return "gemini"

    # Fallback: Groq
    if os.environ.get("GROQ_API_KEY"):
        return "groq"

    # Last resort: local
    local = _get_provider("local")
    if local.is_available():
        return "local"

    # Nothing available — return gemini anyway, it will fail with a clear error
    return "gemini"


async def transcribe_audio_buffer(
    buffer_data: bytes,
    language: str = "id",
) -> List[Dict]:
    """
    Unified transcription entry point.

    Auto-selects the best available provider and transcribes.
    Returns segments as plain dicts for backward compatibility.
    """
    provider_name = _select_provider()
    provider = _get_provider(provider_name)

    logger.info("Transcription backend: %s", provider_name)

    segments = await provider.transcribe(buffer_data, language)

    # Return as plain dicts for backward compat with existing code
    return [
        {
            "start": s["start"],
            "end": s["end"],
            "text": s["text"],
            **({"speaker": s["speaker"]} if s.get("speaker") else {}),
        }
        for s in segments
    ]


def get_provider_info() -> dict:
    """Get info about the currently selected provider."""
    provider_name = _select_provider()
    provider = _get_provider(provider_name)
    return {
        "selected": provider_name,
        **provider.get_info(),
        "all_providers": {
            name: _get_provider(name).get_info()
            for name in ["gemini", "groq", "modal", "local"]
        },
    }
