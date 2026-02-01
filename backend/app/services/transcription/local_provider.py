"""
Local faster-whisper transcription provider.

Dev/fallback provider using local Whisper model.
Requires `faster-whisper` package.
"""

import logging
import os
from typing import List

from app.services.transcription.base import (
    TranscriptionProvider,
    TranscriptSegment,
    ensure_wav,
    safe_remove,
)

logger = logging.getLogger(__name__)


class LocalTranscriptionProvider(TranscriptionProvider):
    """Local faster-whisper transcription (dev fallback)."""

    name = "local"
    supports_diarization = False

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info("Loading local Whisper model '%s' ...", self.model_size)
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("Whisper model ready")
        return self._model

    def is_available(self) -> bool:
        try:
            import faster_whisper  # noqa: F401
            return True
        except ImportError:
            return False

    def get_info(self) -> dict:
        return {
            **super().get_info(),
            "model_size": self.model_size,
            "device": self.device,
        }

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "id",
    ) -> List[TranscriptSegment]:
        wav_path = None
        try:
            wav_path = ensure_wav(audio_bytes)
            if not wav_path or not os.path.exists(wav_path):
                return []
            if os.path.getsize(wav_path) < 4000:
                return []

            segments, _ = self.model.transcribe(
                wav_path,
                language=language,
                vad_filter=True,
                beam_size=5,
            )
            return [
                TranscriptSegment(
                    start=seg.start,
                    end=seg.end,
                    text=seg.text.strip(),
                    speaker="",
                )
                for seg in segments
                if seg.text.strip()
            ]
        except Exception:
            logger.exception("Local transcription error")
            return []
        finally:
            if wav_path:
                safe_remove(wav_path)
