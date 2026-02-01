"""
Groq Whisper API transcription provider.

Uses Whisper Large V3 via Groq's fast inference.
Good quality, returns timestamps, but no native diarization.
"""

import logging
import os
from typing import List

import httpx

from app.services.transcription.base import (
    TranscriptionProvider,
    TranscriptSegment,
    ensure_wav,
    safe_remove,
)

logger = logging.getLogger(__name__)

GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


class GroqTranscriptionProvider(TranscriptionProvider):
    """Groq Whisper API for transcription."""

    name = "groq"
    supports_diarization = False

    def is_available(self) -> bool:
        return bool(os.environ.get("GROQ_API_KEY"))

    def get_info(self) -> dict:
        return {
            **super().get_info(),
            "model": "whisper-large-v3",
            "endpoint": GROQ_WHISPER_URL,
        }

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "id",
    ) -> List[TranscriptSegment]:
        api_key = os.environ.get("GROQ_API_KEY", "")
        wav_path = None

        try:
            wav_path = ensure_wav(audio_bytes)
            if not wav_path or not os.path.exists(wav_path):
                return []
            if os.path.getsize(wav_path) < 4000:
                return []

            async with httpx.AsyncClient(timeout=30.0) as client:
                with open(wav_path, "rb") as audio_file:
                    resp = await client.post(
                        GROQ_WHISPER_URL,
                        headers={"Authorization": f"Bearer {api_key}"},
                        files={"file": ("audio.wav", audio_file, "audio/wav")},
                        data={
                            "model": "whisper-large-v3",
                            "language": language,
                            "response_format": "verbose_json",
                            "timestamp_granularities[]": "segment",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()

            segments = data.get("segments", [])
            return [
                TranscriptSegment(
                    start=s["start"],
                    end=s["end"],
                    text=s["text"].strip(),
                    speaker="",
                )
                for s in segments
                if s.get("text", "").strip()
            ]

        except Exception:
            logger.exception("Groq transcription error")
            return []
        finally:
            if wav_path:
                safe_remove(wav_path)
