"""
Transcription service with three backends (priority order):
1. Gemini 2.5 Flash Lite via OpenRouter (cheap cloud, default)
2. Groq Whisper API (cloud, if GROQ_API_KEY set)
3. Local faster-whisper (dev fallback)

Auto-selects: OpenRouter first (always available), then Groq, then local.
"""

import base64
import subprocess
import tempfile
import os
import wave
import logging
import math
from typing import Optional, List, Dict

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gemini via OpenRouter (primary cloud backend)
# ---------------------------------------------------------------------------

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_TRANSCRIPTION_MODEL = "google/gemini-2.5-flash-lite"

# Max audio chunk size ~20MB base64 (~15MB raw)
MAX_CHUNK_BYTES = 15 * 1024 * 1024


async def _transcribe_via_gemini(
    audio_bytes: bytes,
    language: str = "id",
    api_key: str = "",
) -> List[Dict]:
    """Send audio to Gemini via OpenRouter multimodal API for transcription."""
    wav_path: Optional[str] = None

    try:
        # Convert to WAV if needed
        wav_path = _ensure_wav(audio_bytes)
        if not wav_path or not os.path.exists(wav_path):
            return []
        if os.path.getsize(wav_path) < 4000:
            return []

        file_size = os.path.getsize(wav_path)
        logger.info("Gemini transcription: file size %.1f MB", file_size / 1024 / 1024)

        # For large files, chunk and transcribe
        if file_size > MAX_CHUNK_BYTES:
            return await _transcribe_chunked_gemini(wav_path, language, api_key)

        # Read and encode
        with open(wav_path, "rb") as f:
            audio_data = f.read()
        audio_b64 = base64.b64encode(audio_data).decode("utf-8")

        return await _call_gemini_transcribe(audio_b64, language, api_key)

    except Exception:
        logger.exception("Gemini transcription error")
        return []
    finally:
        if wav_path:
            _safe_remove(wav_path)


async def _call_gemini_transcribe(
    audio_b64: str,
    language: str,
    api_key: str,
    chunk_index: int = 0,
) -> List[Dict]:
    """Call Gemini via OpenRouter with base64 audio for transcription."""
    lang_names = {
        "id": "Bahasa Indonesia",
        "en": "English",
        "es": "Spanish",
        "ms": "Malay",
    }
    lang_name = lang_names.get(language, language)

    prompt = (
        f"Transcribe this audio recording accurately and completely. "
        f"The primary language is {lang_name}. "
        f"Return ONLY the transcription text, nothing else. "
        f"Preserve the original language — do not translate. "
        f"Include all speech, including filler words. "
        f"If there are multiple speakers, indicate speaker changes with newlines. "
        f"Do not add timestamps, annotations, or commentary."
    )

    payload = {
        "model": GEMINI_TRANSCRIPTION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": audio_b64,
                            "format": "wav",
                        },
                    },
                ],
            }
        ],
        "temperature": 0.0,
        "max_tokens": 16000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)

        if resp.status_code != 200:
            logger.error(
                "Gemini transcription error %s: %s",
                resp.status_code,
                resp.text[:300],
            )
            return []

        data = resp.json()

    text = data["choices"][0]["message"]["content"].strip()

    # Split into segments by lines
    segments = []
    for i, line in enumerate(text.split("\n")):
        line = line.strip()
        if line:
            segments.append({
                "start": float(i * 5 + chunk_index * 300),  # approximate
                "end": float(i * 5 + 5 + chunk_index * 300),
                "text": line,
            })

    logger.info(
        "Gemini transcribed chunk %d: %d segments, %d chars",
        chunk_index,
        len(segments),
        len(text),
    )
    return segments


async def _transcribe_chunked_gemini(
    wav_path: str,
    language: str,
    api_key: str,
) -> List[Dict]:
    """Split large audio into chunks and transcribe each via Gemini."""
    file_size = os.path.getsize(wav_path)
    num_chunks = math.ceil(file_size / MAX_CHUNK_BYTES)
    logger.info("Splitting audio into %d chunks for Gemini", num_chunks)

    all_segments: List[Dict] = []

    with open(wav_path, "rb") as f:
        # Read WAV header
        header = f.read(44)  # Standard WAV header
        remaining = file_size - 44
        chunk_size = remaining // num_chunks

        for i in range(num_chunks):
            # Read chunk
            if i == num_chunks - 1:
                chunk_data = f.read()  # Last chunk gets remainder
            else:
                chunk_data = f.read(chunk_size)

            # Create a proper WAV from chunk
            chunk_wav_path = tempfile.mktemp(suffix=".wav")
            try:
                with wave.open(chunk_wav_path, "wb") as wf:
                    # Copy params from original WAV header
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(16000)
                    wf.writeframes(chunk_data)

                with open(chunk_wav_path, "rb") as cf:
                    chunk_audio = cf.read()

                chunk_b64 = base64.b64encode(chunk_audio).decode("utf-8")
                segments = await _call_gemini_transcribe(
                    chunk_b64, language, api_key, chunk_index=i
                )
                all_segments.extend(segments)
            finally:
                _safe_remove(chunk_wav_path)

    return all_segments


# ---------------------------------------------------------------------------
# Groq Whisper API backend (cloud, legacy)
# ---------------------------------------------------------------------------

GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


async def _transcribe_via_groq(
    audio_bytes: bytes,
    language: str = "id",
    api_key: str = "",
) -> List[Dict]:
    """Send audio to Groq Whisper API and return segments."""
    wav_path: Optional[str] = None

    try:
        wav_path = _ensure_wav(audio_bytes)
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
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in segments
            if s.get("text", "").strip()
        ]

    except Exception:
        logger.exception("Groq transcription error")
        return []
    finally:
        if wav_path:
            _safe_remove(wav_path)


# ---------------------------------------------------------------------------
# Local faster-whisper backend (dev fallback)
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
            temp_wav_path = _ensure_wav(buffer_data)
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


def _ensure_wav(audio_bytes: bytes) -> Optional[str]:
    """Convert audio bytes to a WAV file, handling various input formats."""
    if audio_bytes[:4] == b"\x1aE\xdf\xa3":  # WebM
        webm_path = tempfile.mktemp(suffix=".webm")
        with open(webm_path, "wb") as f:
            f.write(audio_bytes)
        try:
            wav_path = _convert_to_wav(webm_path)
        finally:
            _safe_remove(webm_path)
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
            wav_path = _convert_to_wav(tmp_path)
        except Exception:
            _safe_remove(tmp_path)
            # Fallback: treat as raw PCM
            wav_path = tempfile.mktemp(suffix=".wav")
            with wave.open(wav_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)
        else:
            _safe_remove(tmp_path)
        return wav_path


def _convert_to_wav(input_path: str) -> str:
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


def _safe_remove(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Unified interface
# ---------------------------------------------------------------------------

_local_service: Optional[LocalTranscriptionService] = None


def _get_backend() -> str:
    """
    Select transcription backend:
    1. 'gemini' — always available (uses OPENROUTER_API_KEY)
    2. 'groq' — if GROQ_API_KEY is explicitly set
    3. 'local' — if TRANSCRIPTION_BACKEND=local is set (dev only)
    """
    explicit = os.environ.get("TRANSCRIPTION_BACKEND", "").lower()
    if explicit == "local":
        return "local"
    if explicit == "groq" and os.environ.get("GROQ_API_KEY"):
        return "groq"
    # Default: gemini via OpenRouter
    return "gemini"


async def transcribe_audio_buffer(
    buffer_data: bytes,
    language: str = "id",
) -> List[Dict]:
    """
    Unified transcription entry point.
    - Gemini 2.5 Flash Lite via OpenRouter (default, cheap)
    - Groq Whisper API (if GROQ_API_KEY set and TRANSCRIPTION_BACKEND=groq)
    - Local faster-whisper (if TRANSCRIPTION_BACKEND=local)
    """
    backend = _get_backend()
    logger.info("Transcription backend: %s", backend)

    if backend == "gemini":
        settings = get_settings()
        return await _transcribe_via_gemini(
            buffer_data, language, settings.openrouter_api_key
        )
    elif backend == "groq":
        key = os.environ.get("GROQ_API_KEY", "")
        return await _transcribe_via_groq(buffer_data, language, key)
    else:
        global _local_service
        if _local_service is None:
            _local_service = LocalTranscriptionService()
        return _local_service.transcribe_buffer(buffer_data, language)
