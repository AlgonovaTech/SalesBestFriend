"""
AI-based call stage detection.
Ported from call_structure_config.detect_stage_by_context
and trial_class_analyzer.detect_current_stage.
"""

import json
import logging
from typing import List, Dict, Tuple, Optional

from app.services.llm.base import get_llm_client

logger = logging.getLogger(__name__)


def detect_stage(
    conversation_text: str,
    stages: List[Dict],
    elapsed_seconds: int,
    previous_stage_id: Optional[str] = None,
    min_confidence: float = 0.6,
) -> str:
    """
    Detect current call stage from conversation context.

    Falls back to time-based detection on low confidence or error.
    """
    if not stages:
        return ""

    if len(conversation_text.strip()) < 100:
        return stages[0]["id"]

    try:
        stage_id, confidence = _ai_detect(
            conversation_text, stages, elapsed_seconds,
        )

        if confidence >= min_confidence:
            return stage_id

        if previous_stage_id and confidence < min_confidence:
            return previous_stage_id

        return _time_based_fallback(stages, elapsed_seconds)

    except Exception as exc:
        logger.warning("Stage detection error: %s, using fallback", exc)
        return _time_based_fallback(stages, elapsed_seconds)


def _ai_detect(
    conversation_text: str,
    stages: List[Dict],
    elapsed_seconds: int,
) -> Tuple[str, float]:
    """Use LLM to detect stage. Returns ``(stage_id, confidence)``."""
    stage_descs = []
    for i, s in enumerate(stages):
        items_text = "\n".join(
            f"- {it['content']}" for it in s.get("items", [])[:3]
        )
        extra = len(s.get("items", [])) - 3
        if extra > 0:
            items_text += f"\n- ...and {extra} more"
        t0 = s["startOffsetSeconds"] // 60
        t1 = (s["startOffsetSeconds"] + s["durationSeconds"]) // 60
        stage_descs.append(
            f"{i + 1}. **{s['name']}** (recommended: {t0}-{t1} min)\n   {items_text}"
        )

    prompt = f"""Analyzing a sales call in Bahasa Indonesia to determine current stage.

Elapsed: {elapsed_seconds // 60}m {elapsed_seconds % 60}s (reference only)

Recent conversation:
{conversation_text}

Stages:
{chr(10).join(stage_descs)}

Based on CONTENT (not just time), which stage? Be confident, avoid jitter.

Return JSON: {{"stage_id": "...", "confidence": 0.0-1.0, "reasoning": "..."}}
"""

    llm = get_llm_client()
    raw = llm.call(prompt, temperature=0.2, max_tokens=200)
    result = json.loads(raw)
    if "error" in result:
        raise RuntimeError(result.get("details", "API error"))

    stage_id = result.get("stage_id", "")
    confidence = result.get("confidence", 0.0)

    valid_ids = {s["id"] for s in stages}
    if stage_id not in valid_ids:
        return stages[0]["id"], 0.5

    return stage_id, confidence


def _time_based_fallback(stages: List[Dict], elapsed_seconds: int) -> str:
    for stage in reversed(stages):
        if elapsed_seconds >= stage["startOffsetSeconds"]:
            return stage["id"]
    return stages[0]["id"] if stages else ""


def get_stage_timing_status(
    stage_id: str,
    elapsed_seconds: int,
    stages: List[Dict],
) -> Dict[str, str]:
    """Return ``{"status": ..., "message": ...}`` for timing display."""
    stage = next((s for s in stages if s["id"] == stage_id), None)
    if not stage:
        return {"status": "unknown", "message": "Stage not found"}

    start = stage["startOffsetSeconds"]
    end = start + stage["durationSeconds"]

    if elapsed_seconds < start:
        return {"status": "not_started", "message": f"Starts in {(start - elapsed_seconds) // 60} min"}
    if elapsed_seconds <= end:
        return {"status": "on_time", "message": "On track"}
    if elapsed_seconds <= end + 120:
        return {"status": "slightly_late", "message": "Slightly behind"}
    return {"status": "very_late", "message": f"{(elapsed_seconds - end) // 60} min behind"}
