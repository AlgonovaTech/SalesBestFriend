"""
Modal.com transcription + diarization provider.

Uses the existing Modal microservice deployed by the team for:
- High-quality transcription (Whisper-based)
- Speaker diarization (speaker separation)

This is the ONLY provider that supports native diarization.

Configuration:
    MODAL_TRANSCRIPTION_ENDPOINT - Full URL to the Modal endpoint
    MODAL_API_TOKEN - Bearer token for auth (optional, depends on Modal setup)

Expected Modal API contract:
    POST /transcribe
    Content-Type: multipart/form-data
    Body: file (audio), language (str), num_speakers (int, optional)

    Response JSON:
    {
        "segments": [
            {
                "start": 0.0,
                "end": 5.2,
                "text": "Hello, how are you?",
                "speaker": "Speaker 1",
                "confidence": 0.95
            },
            ...
        ],
        "language": "id",
        "duration": 120.5,
        "num_speakers": 2
    }
"""

import logging
import os
from typing import List, Optional

import httpx

from app.services.transcription.base import (
    TranscriptionProvider,
    TranscriptSegment,
    DiarizationSegment,
    ensure_wav,
    safe_remove,
)

logger = logging.getLogger(__name__)


class ModalTranscriptionProvider(TranscriptionProvider):
    """Modal.com transcription + diarization service."""

    name = "modal"
    supports_diarization = True

    def __init__(self):
        # Try config first, then env vars
        try:
            from app.config import get_settings
            settings = get_settings()
            self.endpoint = settings.modal_transcription_endpoint or os.environ.get("MODAL_TRANSCRIPTION_ENDPOINT", "")
            self.api_token = settings.modal_api_token or os.environ.get("MODAL_API_TOKEN", "")
        except Exception:
            self.endpoint = os.environ.get("MODAL_TRANSCRIPTION_ENDPOINT", "")
            self.api_token = os.environ.get("MODAL_API_TOKEN", "")

    def is_available(self) -> bool:
        return bool(self.endpoint)

    def get_info(self) -> dict:
        return {
            **super().get_info(),
            "endpoint": self.endpoint or "(not configured)",
            "has_token": bool(self.api_token),
        }

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "id",
    ) -> List[TranscriptSegment]:
        """Basic transcription without diarization."""
        diarized = await self.transcribe_with_diarization(audio_bytes, language)
        return [
            TranscriptSegment(
                start=s["start"],
                end=s["end"],
                text=s["text"],
                speaker=s.get("speaker", ""),
            )
            for s in diarized
        ]

    async def transcribe_with_diarization(
        self,
        audio_bytes: bytes,
        language: str = "id",
        num_speakers: Optional[int] = None,
    ) -> List[DiarizationSegment]:
        """
        Transcribe with speaker diarization via Modal endpoint.

        The Modal service handles both Whisper transcription and
        pyannote/speaker-diarization in a single request.
        """
        if not self.endpoint:
            logger.error("Modal endpoint not configured")
            return []

        wav_path = None
        try:
            wav_path = ensure_wav(audio_bytes)
            if not wav_path or not os.path.exists(wav_path):
                return []

            headers = {}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"

            form_data = {"language": language}
            if num_speakers is not None:
                form_data["num_speakers"] = str(num_speakers)

            async with httpx.AsyncClient(timeout=600.0) as client:
                with open(wav_path, "rb") as audio_file:
                    resp = await client.post(
                        f"{self.endpoint.rstrip('/')}/transcribe",
                        headers=headers,
                        files={"file": ("audio.wav", audio_file, "audio/wav")},
                        data=form_data,
                    )
                    resp.raise_for_status()
                    data = resp.json()

            segments = data.get("segments", [])
            logger.info(
                "Modal transcription: %d segments, %d speakers, %.1fs duration",
                len(segments),
                data.get("num_speakers", 0),
                data.get("duration", 0),
            )

            return [
                DiarizationSegment(
                    start=s.get("start", 0.0),
                    end=s.get("end", 0.0),
                    text=s.get("text", "").strip(),
                    speaker=s.get("speaker", ""),
                    confidence=s.get("confidence", 0.0),
                )
                for s in segments
                if s.get("text", "").strip()
            ]

        except httpx.ConnectError:
            logger.error("Cannot connect to Modal endpoint: %s", self.endpoint)
            return []
        except httpx.HTTPStatusError as e:
            logger.error("Modal API error %s: %s", e.response.status_code, e.response.text[:300])
            return []
        except Exception:
            logger.exception("Modal transcription error")
            return []
        finally:
            if wav_path:
                safe_remove(wav_path)
