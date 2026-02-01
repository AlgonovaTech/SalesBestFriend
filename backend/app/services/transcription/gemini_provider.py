"""
Gemini 2.5 Flash Lite transcription via OpenRouter.

Primary provider — always available if OPENROUTER_API_KEY is set.
Cheap and fast, but no native diarization.
"""

import base64
import logging
import math
import os
import wave
import tempfile
from typing import List

import httpx

from app.config import get_settings
from app.services.transcription.base import (
    TranscriptionProvider,
    TranscriptSegment,
    ensure_wav,
    safe_remove,
)

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_TRANSCRIPTION_MODEL = "google/gemini-2.5-flash-lite"
MAX_CHUNK_BYTES = 15 * 1024 * 1024  # ~15MB raw → ~20MB base64


class GeminiTranscriptionProvider(TranscriptionProvider):
    """Gemini via OpenRouter for transcription."""

    name = "gemini"
    supports_diarization = False

    def is_available(self) -> bool:
        try:
            settings = get_settings()
            return bool(settings.openrouter_api_key)
        except Exception:
            return False

    def get_info(self) -> dict:
        return {
            **super().get_info(),
            "model": GEMINI_TRANSCRIPTION_MODEL,
            "endpoint": OPENROUTER_URL,
            "max_chunk_bytes": MAX_CHUNK_BYTES,
        }

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "id",
    ) -> List[TranscriptSegment]:
        settings = get_settings()
        api_key = settings.openrouter_api_key
        wav_path = None

        try:
            wav_path = ensure_wav(audio_bytes)
            if not wav_path or not os.path.exists(wav_path):
                return []
            if os.path.getsize(wav_path) < 4000:
                return []

            file_size = os.path.getsize(wav_path)
            logger.info("Gemini transcription: file size %.1f MB", file_size / 1024 / 1024)

            if file_size > MAX_CHUNK_BYTES:
                return await self._transcribe_chunked(wav_path, language, api_key)

            with open(wav_path, "rb") as f:
                audio_data = f.read()
            audio_b64 = base64.b64encode(audio_data).decode("utf-8")

            return await self._call_gemini(audio_b64, language, api_key)

        except Exception:
            logger.exception("Gemini transcription error")
            return []
        finally:
            if wav_path:
                safe_remove(wav_path)

    async def _call_gemini(
        self,
        audio_b64: str,
        language: str,
        api_key: str,
        chunk_index: int = 0,
    ) -> List[TranscriptSegment]:
        lang_names = {
            "id": "Bahasa Indonesia",
            "en": "English",
            "es": "Spanish",
            "ms": "Malay",
            "vi": "Vietnamese",
            "tl": "Filipino/Tagalog",
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

        segments = []
        for i, line in enumerate(text.split("\n")):
            line = line.strip()
            if line:
                segments.append(
                    TranscriptSegment(
                        start=float(i * 5 + chunk_index * 300),
                        end=float(i * 5 + 5 + chunk_index * 300),
                        text=line,
                        speaker="",
                    )
                )

        logger.info(
            "Gemini transcribed chunk %d: %d segments, %d chars",
            chunk_index,
            len(segments),
            len(text),
        )
        return segments

    async def _transcribe_chunked(
        self,
        wav_path: str,
        language: str,
        api_key: str,
    ) -> List[TranscriptSegment]:
        file_size = os.path.getsize(wav_path)
        num_chunks = math.ceil(file_size / MAX_CHUNK_BYTES)
        logger.info("Splitting audio into %d chunks for Gemini", num_chunks)

        all_segments: List[TranscriptSegment] = []

        with open(wav_path, "rb") as f:
            header = f.read(44)
            remaining = file_size - 44
            chunk_size = remaining // num_chunks

            for i in range(num_chunks):
                if i == num_chunks - 1:
                    chunk_data = f.read()
                else:
                    chunk_data = f.read(chunk_size)

                chunk_wav_path = tempfile.mktemp(suffix=".wav")
                try:
                    with wave.open(chunk_wav_path, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(16000)
                        wf.writeframes(chunk_data)

                    with open(chunk_wav_path, "rb") as cf:
                        chunk_audio = cf.read()

                    chunk_b64 = base64.b64encode(chunk_audio).decode("utf-8")
                    segments = await self._call_gemini(
                        chunk_b64, language, api_key, chunk_index=i
                    )
                    all_segments.extend(segments)
                finally:
                    safe_remove(chunk_wav_path)

        return all_segments
