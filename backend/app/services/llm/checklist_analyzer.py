"""
Checklist item completion detection via LLM.
Ported from trial_class_analyzer.check_checklist_item + guards.
"""

import json
import logging
from typing import Dict, List, Tuple

from app.services.llm.base import get_llm_client

logger = logging.getLogger(__name__)


def check_checklist_item(
    item: Dict,
    conversation_text: str,
) -> Tuple[bool, float, str, Dict]:
    """
    Check if a checklist item has been completed.

    Args:
        item: ``{id, content, type, extended_description, semantic_keywords}``
        conversation_text: Recent conversation (Indonesian).

    Returns:
        ``(completed, confidence, evidence, debug_info)``
    """
    if len(conversation_text.strip()) < 30:
        return False, 0.0, "Insufficient context", {
            "stage": "guard_context_too_short",
        }

    item_id = item["id"]
    item_content = item["content"]
    item_type = item.get("type", "discuss")
    extended_description = item.get("extended_description", "")
    semantic_keywords = item.get("semantic_keywords", {})

    # Guard 0: pre-filter with keywords
    if semantic_keywords:
        ok, kw_debug = _prefilter_keywords(conversation_text, semantic_keywords)
        if not ok:
            return False, 0.0, "Pre-filter failed", {
                "stage": "guard_0_prefilter_failed",
                "keywords_debug": kw_debug,
            }

    # Build LLM prompt
    type_block = _type_specific_prompt(item_type)

    prompt = f"""You are a STRICT quality checker analyzing a sales call in Bahasa Indonesia.

TASK: Check if this action was completed:
Action: "{item_content}"

ADDITIONAL CONTEXT: {extended_description}

Recent conversation (Bahasa Indonesia):
{conversation_text}

{type_block}

CRITICAL VALIDATION RULES:
1. Evidence must be a DIRECT QUOTE from conversation
2. Evidence must CLEARLY show the action was done
3. Generic phrases like "oke", "baik", "ya" are NEVER valid
4. Promises ("nanti", "akan") are NOT completion
5. If even 20% unsure -> completed=false

CONFIDENCE: 90-100% perfect, 70-89% good, 50-69% weak, <50% not done.

Return ONLY valid JSON:
{{
  "completed": true/false,
  "confidence": 0.0-1.0,
  "evidence": "exact quote (empty if not completed)",
  "reasoning": "why"
}}
"""

    llm = get_llm_client()

    try:
        raw = llm.call(prompt, temperature=0.2, max_tokens=200)
        result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(result.get("details", "API error"))

        completed = result.get("completed", False)
        confidence = result.get("confidence", 0.0)
        evidence = result.get("evidence", "")
        reasoning = result.get("reasoning", "")

        debug_info: Dict = {
            "stage": "initial_check",
            "first_completed": completed,
            "first_confidence": confidence,
            "first_evidence": evidence,
            "first_reasoning": reasoning,
        }

        # Guard 1: confidence threshold
        if completed and confidence < 0.7:
            debug_info["stage"] = "guard_1_low_confidence"
            return False, confidence, "Confidence too low", debug_info

        # Guard 2: evidence length
        if completed and len(evidence.strip()) < 10:
            debug_info["stage"] = "guard_2_evidence_too_short"
            return False, confidence, "Evidence too short", debug_info

        # Guard 3: second-pass validation
        if completed and confidence >= 0.7:
            valid = _validate_evidence(item_content, evidence, reasoning, item_type)
            debug_info["validation_passed"] = valid
            if not valid:
                debug_info["stage"] = "guard_3_validation_failed"
                return False, confidence, f"Evidence not relevant: {evidence[:100]}", debug_info

        debug_info["stage"] = "accepted"
        return completed, confidence, evidence, debug_info

    except Exception as exc:
        logger.warning("Checklist check failed for %s: %s", item_id, exc)
        return False, 0.0, str(exc), {"stage": "error", "error": str(exc)}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prefilter_keywords(
    text: str, keywords: Dict[str, List[str]],
) -> Tuple[bool, Dict]:
    text_lower = text.lower()
    required = keywords.get("required", [])
    forbidden = keywords.get("forbidden", [])
    debug: Dict = {"required": required, "forbidden": forbidden, "found_required": [], "found_forbidden": []}

    if required:
        found = [kw for kw in required if kw.lower() in text_lower]
        debug["found_required"] = found
        if not found:
            return False, debug

    if forbidden:
        found = [kw for kw in forbidden if kw.lower() in text_lower]
        debug["found_forbidden"] = found
        if found:
            return False, debug

    return True, debug


def _type_specific_prompt(item_type: str) -> str:
    if item_type == "discuss":
        return """TYPE: DISCUSS/ASK — find a QUESTION or an ANSWER proving the question was asked.
GOOD: "Anaknya umur berapa?" or "Anaknya 8 tahun" (answer proves question).
BAD: "Anak suka belajar" (no question about age)."""
    return """TYPE: SAY/EXPLAIN — find the manager STATING or EXPLAINING something.
GOOD: "Platform kami seperti game interaktif untuk belajar coding" (explanation).
BAD: "Mau tau cara kerja platform?" (asking, not explaining)."""


INVALID_PHRASES = [
    "oke", "ok", "baik", "ya", "halo", "hai",
    "selamat pagi", "selamat siang", "selamat datang",
    "terima kasih", "sama-sama", "silakan", "gimana", "apa kabar",
]

INTRODUCTION_PATTERNS = [
    "nama saya", "saya adalah", "perkenalkan",
    "kenalkan", "mr.", "ms.", "tutor", "teacher", "guru",
]


def _validate_evidence(
    item_content: str,
    evidence: str,
    reasoning: str,
    item_type: str,
) -> bool:
    if not evidence or len(evidence.strip()) < 5:
        return False

    ev_lower = evidence.lower().strip()

    # Reject introductions (unless action is about introductions)
    if any(p in ev_lower for p in INTRODUCTION_PATTERNS):
        action_lower = item_content.lower()
        if not any(w in action_lower for w in ["greet", "introduce", "perkenalkan", "salam"]):
            return False

    # Reject if evidence is only a generic phrase
    for phrase in INVALID_PHRASES:
        if ev_lower == phrase or ev_lower == phrase + ".":
            return False

    if len(evidence.split()) < 3:
        return False

    # Second LLM validation
    type_check = (
        "DISCUSS/ASK: evidence must show a QUESTION or an ANSWER implying the question."
        if item_type == "discuss"
        else "SAY/EXPLAIN: evidence must show the manager STATING or EXPLAINING."
    )

    validation_prompt = f"""STRICT evidence validator for a sales call checklist.

ACTION: "{item_content}"
EVIDENCE: "{evidence}"
REASONING: "{reasoning}"

{type_check}

Checks: 1) actual content, 2) semantic match, 3) specific enough, 4) matches type.
BE EXTREMELY STRICT. Return ONLY JSON: {{"is_valid": true/false, "explanation": "..."}}
"""

    llm = get_llm_client()
    try:
        raw = llm.call(validation_prompt, temperature=0.05, max_tokens=150)
        result = json.loads(raw)
        if "error" in result:
            return False
        return bool(result.get("is_valid", False))
    except Exception:
        return False
