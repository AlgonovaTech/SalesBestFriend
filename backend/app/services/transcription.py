"""
Real-time transcription service using faster-whisper.
Handles WebM, WAV, and raw PCM audio formats.

Ported from utils/realtime_transcriber.py.
"""

import subprocess
import tempfile
import os
import wave
import logging
from typing import Optional, List, Dict

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Transcribe audio using Whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            logger.info("Loading Whisper model '%s' ...", self.model_size)
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("Whisper model ready")
        return self._model

    # ------------------------------------------------------------------
    # Format helpers
    # ------------------------------------------------------------------

    @staticmethod
    def convert_webm_to_wav(webm_path: str, tolerant: bool = False) -> str:
        wav_path = webm_path.replace(".webm", ".wav")
        cmd = [
            "ffmpeg",
            "-loglevel", "warning" if tolerant else "error",
        ]
        if tolerant:
            cmd += ["-err_detect", "ignore_err", "-fflags", "+genpts+igndts"]
        cmd += [
            "-i", webm_path,
            "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le",
            "-y", wav_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
            raise RuntimeError(f"WAV file too small or missing: {wav_path}")
        return wav_path

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    def transcribe_buffer(
        self,
        buffer_data: bytes,
        language: str = "id",
    ) -> List[Dict]:
        """
        Transcribe raw audio bytes (WebM / WAV / PCM Int16).

        Returns ``[{"start": float, "end": float, "text": str}, ...]``.
        """
        temp_wav_path = None

        try:
            if buffer_data[:4] == b"RIFF":
                temp_wav_path = tempfile.mktemp(suffix=".wav")
                with open(temp_wav_path, "wb") as f:
                    f.write(buffer_data)

            elif buffer_data[:4] == b"\x1aE\xdf\xa3":  # EBML / WebM
                temp_webm = tempfile.mktemp(suffix=".webm")
                with open(temp_webm, "wb") as f:
                    f.write(buffer_data)
                try:
                    temp_wav_path = self.convert_webm_to_wav(
                        temp_webm, tolerant=True,
                    )
                finally:
                    _safe_remove(temp_webm)

            else:
                # Raw PCM Int16, 16 kHz mono
                temp_wav_path = tempfile.mktemp(suffix=".wav")
                with wave.open(temp_wav_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(buffer_data)

            if not temp_wav_path or not os.path.exists(temp_wav_path):
                return []

            if os.path.getsize(temp_wav_path) < 4000:
                return []

            segments, _ = self.model.transcribe(
                temp_wav_path,
                language=language,
                vad_filter=True,
                beam_size=5,
            )

            return [
                {"start": seg.start, "end": seg.end, "text": seg.text.strip()}
                for seg in segments
                if seg.text.strip()
            ]

        except Exception:
            logger.exception("Transcription error")
            return []

        finally:
            if temp_wav_path:
                _safe_remove(temp_wav_path)


def _safe_remove(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


# Singleton -----------------------------------------------------------------

_service: Optional[TranscriptionService] = None


def get_transcription_service(model_size: str = "base") -> TranscriptionService:
    global _service
    if _service is None:
        _service = TranscriptionService(model_size=model_size)
    return _service


def transcribe_audio_buffer(
    buffer_data: bytes, language: str = "id",
) -> List[Dict]:
    """Convenience wrapper."""
    return get_transcription_service().transcribe_buffer(buffer_data, language)
