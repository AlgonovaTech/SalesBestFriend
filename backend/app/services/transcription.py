"""
Transcription service with two backends:
1. Groq Whisper API (cloud, lightweight — used on Railway)
2. Local faster-whisper (for dev / GPU machines)

Auto-selects based on GROQ_API_KEY presence.
"""

import subprocess
import tempfile
import os
import wave
import logging
from typing import Optional, List, Dict

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Groq Whisper API backend (cloud)
# ---------------------------------------------------------------------------

GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


async def _transcribe_via_groq(
    audio_bytes: bytes,
    language: str = "id",
    api_key: str = "",
) -> List[Dict]:
    """Send audio to Groq Whisper API and return segments."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_path: Optional[str] = None

    try:
        # Convert to WAV if needed
        if audio_bytes[:4] == b"\x1aE\xdf\xa3":  # WebM
            webm_path = tmp.name.replace(".wav", ".webm")
            with open(webm_path, "wb") as f:
                f.write(audio_bytes)
            wav_path = _convert_webm_to_wav(webm_path)
            _safe_remove(webm_path)
        elif audio_bytes[:4] == b"RIFF":
            wav_path = tmp.name
            with open(wav_path, "wb") as f:
                f.write(audio_bytes)
        else:
            # Raw PCM → WAV
            wav_path = tmp.name
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)

        if not wav_path or not os.path.exists(wav_path):
            return []
        if os.path.getsize(wav_path) < 4000:
            return []

        # Call Groq API
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
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in segments
            if s.get("text", "").strip()
        ]

    except Exception:
        logger.exception("Groq transcription error")
        return []
    finally:
        tmp.close()
        if wav_path:
            _safe_remove(wav_path)


# ---------------------------------------------------------------------------
# Local faster-whisper backend (dev)
# ---------------------------------------------------------------------------


class LocalTranscriptionService:
    """Transcribe audio using local faster-whisper model."""

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

    def transcribe_buffer(
        self,
        buffer_data: bytes,
        language: str = "id",
    ) -> List[Dict]:
        temp_wav_path = None
        try:
            if buffer_data[:4] == b"RIFF":
                temp_wav_path = tempfile.mktemp(suffix=".wav")
                with open(temp_wav_path, "wb") as f:
                    f.write(buffer_data)
            elif buffer_data[:4] == b"\x1aE\xdf\xa3":
                temp_webm = tempfile.mktemp(suffix=".webm")
                with open(temp_webm, "wb") as f:
                    f.write(buffer_data)
                try:
                    temp_wav_path = _convert_webm_to_wav(temp_webm)
                finally:
                    _safe_remove(temp_webm)
            else:
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
            logger.exception("Local transcription error")
            return []
        finally:
            if temp_wav_path:
                _safe_remove(temp_wav_path)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _convert_webm_to_wav(webm_path: str) -> str:
    wav_path = webm_path.replace(".webm", ".wav")
    cmd = [
        "ffmpeg",
        "-loglevel", "warning",
        "-err_detect", "ignore_err",
        "-fflags", "+genpts+igndts",
        "-i", webm_path,
        "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le",
        "-y", wav_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
        raise RuntimeError(f"WAV file too small or missing: {wav_path}")
    return wav_path


def _safe_remove(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Unified interface
# ---------------------------------------------------------------------------

_groq_api_key: Optional[str] = os.environ.get("GROQ_API_KEY")
_local_service: Optional[LocalTranscriptionService] = None


def _use_cloud() -> bool:
    """Use Groq API when GROQ_API_KEY is set (Railway deploy)."""
    return bool(os.environ.get("GROQ_API_KEY"))


async def transcribe_audio_buffer(
    buffer_data: bytes,
    language: str = "id",
) -> List[Dict]:
    """
    Unified transcription entry point.
    - Cloud (Groq API) when GROQ_API_KEY is set
    - Local faster-whisper otherwise
    """
    if _use_cloud():
        key = os.environ.get("GROQ_API_KEY", "")
        return await _transcribe_via_groq(buffer_data, language, key)
    else:
        global _local_service
        if _local_service is None:
            _local_service = LocalTranscriptionService()
        return _local_service.transcribe_buffer(buffer_data, language)
