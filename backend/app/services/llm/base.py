"""
OpenRouter LLM client.
Ported from trial_class_analyzer._call_llm.
"""

import json
import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper around the OpenRouter chat-completions API."""

    def __init__(self, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = settings.openrouter_api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model or settings.llm_realtime_model

    def call(
        self,
        prompt: str,
        *,
        temperature: float = 0.5,
        max_tokens: int = 500,
        model: Optional[str] = None,
    ) -> str:
        """
        Send a single-user-message prompt. Returns assistant content.

        On errors returns a JSON string with an ``error`` key.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            resp = httpx.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=300.0,
            )
            if resp.status_code != 200:
                error_body = resp.text[:500]
                logger.error("LLM API error %s: %s", resp.status_code, error_body)
                return json.dumps({"error": "API call failed", "details": f"HTTP {resp.status_code}: {error_body}"})
            data = resp.json()
        except Exception as exc:
            logger.error("LLM API call failed: %s", exc)
            return json.dumps({"error": "API call failed", "details": str(exc)})

        content: str = data["choices"][0]["message"]["content"]

        # Strip markdown fences
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return content.strip()


# Singleton -----------------------------------------------------------------

_client: Optional[LLMClient] = None


def get_llm_client(model: Optional[str] = None) -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient(model=model)
    return _client
