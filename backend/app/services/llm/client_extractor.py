"""
Client card field extraction via LLM.
Ported from trial_class_analyzer.extract_client_card_fields.
"""

import json
import logging
from typing import Dict, List

from app.services.llm.base import get_llm_client

logger = logging.getLogger(__name__)

# Placeholder values the LLM sometimes hallucinates
PLACEHOLDER_VALUES = [
    "tidak disebutkan", "not mentioned", "unknown",
    "tidak ada", "tidak jelas", "belum disebutkan",
    "n/a", "na", "-", "none",
]

INVALID_EVIDENCE_STARTS = [
    "oke,", "ok,", "baik,", "ya,", "halo,", "hai,",
    "selamat pagi", "selamat siang", "selamat datang", "terima kasih",
]


def extract_client_card_fields(
    conversation_text: str,
    current_values: Dict[str, str],
    fields: List[Dict],
    extraction_hints: Dict[str, str],
) -> Dict[str, Dict[str, str]]:
    """
    Extract / update client card fields from conversation.

    Args:
        conversation_text: Recent conversation in Indonesian.
        current_values: ``{field_id: current_value}`` to avoid overwriting.
        fields: List of field definitions with ``id`` and ``label``.
        extraction_hints: ``{field_id: hint_text}``.

    Returns:
        ``{field_id: {"value", "evidence", "confidence", "label"}}``
        Only fields with new information.
    """
    if len(conversation_text.strip()) < 200:
        return {}

    field_descs = []
    for f in fields:
        fid = f["id"]
        label = f["label"]
        hint = extraction_hints.get(fid, "Extract relevant information")
        field_descs.append(f"- {fid} ({label}): {hint}")

    fields_str = "\n".join(field_descs)

    prompt = f"""You are analyzing a sales call in Bahasa Indonesia to extract client information.

Conversation (Bahasa Indonesia):
{conversation_text}

Extract information for these fields (only if clearly mentioned):
{fields_str}

RULES:
1. Only extract if CONFIDENT and EXPLICITLY mentioned
2. Keep extractions brief (1-2 sentences max)
3. If not mentioned, DO NOT INCLUDE the field
4. Conversation is Indonesian; respond in English
5. Evidence MUST be a direct quote
6. NEVER use placeholder values like "Tidak disebutkan", "Unknown", "N/A"
7. If unsure, SKIP the field

Return ONLY valid JSON:
{{
  "field_id": {{
    "value": "extracted text",
    "evidence": "direct quote",
    "confidence": 0.0-1.0
  }}
}}
If nothing found, return: {{}}
"""

    llm = get_llm_client()
    try:
        raw = llm.call(prompt, temperature=0.3, max_tokens=800)
        result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(result.get("details", "API error"))
    except Exception as exc:
        logger.warning("Client card extraction failed: %s", exc)
        return {}

    label_map = {f["id"]: f["label"] for f in fields}
    updates: Dict[str, Dict[str, str]] = {}

    for field_id, field_data in result.items():
        # Skip already-filled fields
        if current_values.get(field_id):
            continue

        if isinstance(field_data, dict):
            value = field_data.get("value", "")
            evidence = field_data.get("evidence", "")
            confidence = field_data.get("confidence", 1.0)
        else:
            value = str(field_data)
            evidence = ""
            confidence = 1.0

        # Guard: reject placeholders
        v_lower = value.lower().strip()
        if v_lower in PLACEHOLDER_VALUES or any(p in v_lower for p in ["tidak di", "not men", "belum di"]):
            continue

        if not value or len(value.strip()) <= 5:
            continue
        if confidence < 0.7:
            continue
        if not evidence or len(evidence.strip()) < 10:
            continue

        # Validate evidence
        field_label = label_map.get(field_id, field_id)
        if not _validate_field_evidence(field_label, value, evidence):
            continue

        updates[field_id] = {
            "value": value.strip(),
            "evidence": evidence.strip(),
            "confidence": confidence,
            "label": field_label,
        }

    return updates


def _validate_field_evidence(
    field_label: str,
    value: str,
    evidence: str,
) -> bool:
    if not evidence or len(evidence.strip()) < 5:
        return False

    ev_lower = evidence.lower().strip()
    for start in INVALID_EVIDENCE_STARTS:
        if ev_lower.startswith(start):
            return False

    if len(evidence.split()) < 3:
        return False

    # Value should appear in evidence (for short values like names)
    v_lower = value.lower().strip()
    if len(value.split()) <= 3 and len(value) > 3:
        words = v_lower.split()
        if sum(1 for w in words if w in ev_lower) == 0:
            return False

    # LLM validation
    prompt = f"""STRICT validator for client info extraction.

FIELD: {field_label}
VALUE: "{value}"
EVIDENCE: "{evidence}"

Is evidence about the CLIENT and does it clearly prove the value?
BE STRICT. Return JSON: {{"is_valid": true/false, "explanation": "..."}}
"""
    llm = get_llm_client()
    try:
        raw = llm.call(prompt, temperature=0.05, max_tokens=150)
        r = json.loads(raw)
        return bool(r.get("is_valid", False))
    except Exception:
        return False
