"""
Base class and shared types for transcription providers.
"""

import logging
import os
import subprocess
import tempfile
import wave
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypedDict

logger = logging.getLogger(__name__)


class TranscriptSegment(TypedDict):
    """Single transcription segment with timing."""
    start: float
    end: float
    text: str
    speaker: str  # "Agent", "Customer", "Speaker 1", etc. Empty if unknown.


class DiarizationSegment(TypedDict):
    """Extended segment with speaker diarization info."""
    start: float
    end: float
    text: str
    speaker: str
    confidence: float


class TranscriptionProvider(ABC):
    """Abstract base for all transcription providers."""

    name: str = "base"
    supports_diarization: bool = False

    @abstractmethod
    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "id",
    ) -> List[TranscriptSegment]:
        """
        Transcribe audio bytes and return segments.

        Args:
            audio_bytes: Raw audio in any common format (WAV, WebM, MP3, etc.)
            language: ISO 639-1 language code

        Returns:
            List of transcript segments with timing
        """
        ...

    async def transcribe_with_diarization(
        self,
        audio_bytes: bytes,
        language: str = "id",
        num_speakers: Optional[int] = None,
    ) -> List[DiarizationSegment]:
        """
        Transcribe with speaker diarization (if supported).
        Falls back to regular transcribe() if not supported.
        """
        segments = await self.transcribe(audio_bytes, language)
        return [
            DiarizationSegment(
                start=s["start"],
                end=s["end"],
                text=s["text"],
                speaker=s.get("speaker", ""),
                confidence=0.0,
            )
            for s in segments
        ]

    def is_available(self) -> bool:
        """Check if this provider has required credentials/dependencies."""
        return True

    def get_info(self) -> dict:
        """Return provider metadata for debugging."""
        return {
            "provider": self.name,
            "supports_diarization": self.supports_diarization,
            "available": self.is_available(),
        }


# ---------------------------------------------------------------------------
# Shared audio helpers (used by all providers)
# ---------------------------------------------------------------------------


def ensure_wav(audio_bytes: bytes) -> Optional[str]:
    """Convert audio bytes to a WAV file, handling various input formats."""
    if audio_bytes[:4] == b"\x1aE\xdf\xa3":  # WebM
        webm_path = tempfile.mktemp(suffix=".webm")
        with open(webm_path, "wb") as f:
            f.write(audio_bytes)
        try:
            wav_path = convert_to_wav(webm_path)
        finally:
            safe_remove(webm_path)
        return wav_path
    elif audio_bytes[:4] == b"RIFF":  # Already WAV
        wav_path = tempfile.mktemp(suffix=".wav")
        with open(wav_path, "wb") as f:
            f.write(audio_bytes)
        return wav_path
    else:
        # Try ffmpeg for any other format (mp3, ogg, flac, etc.)
        tmp_path = tempfile.mktemp(suffix=".bin")
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)
        try:
            wav_path = convert_to_wav(tmp_path)
        except Exception:
            safe_remove(tmp_path)
            # Fallback: treat as raw PCM
            wav_path = tempfile.mktemp(suffix=".wav")
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)
        else:
            safe_remove(tmp_path)
        return wav_path


def convert_to_wav(input_path: str) -> str:
    """Convert any audio format to 16kHz mono WAV using ffmpeg."""
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"
    if wav_path == input_path:
        wav_path = input_path + ".wav"
    cmd = [
        "ffmpeg",
        "-loglevel", "warning",
        "-err_detect", "ignore_err",
        "-fflags", "+genpts+igndts",
        "-i", input_path,
        "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le",
        "-y", wav_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
        raise RuntimeError(f"WAV conversion failed: {wav_path}")
    return wav_path


def safe_remove(path: str):
    """Remove file silently."""
    try:
        os.remove(path)
    except OSError:
        pass
