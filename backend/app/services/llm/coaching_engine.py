"""
Real-time coaching engine.
Generates contextual tips during a live call based on
playbook, pre-call data, and current conversation.
"""

import json
import logging
from typing import Dict, List, Optional

from app.services.llm.base import get_llm_client

logger = logging.getLogger(__name__)


def generate_coaching_tip(
    conversation_text: str,
    current_stage: Dict,
    pre_call_data: Optional[Dict] = None,
    checklist_progress: Optional[Dict[str, bool]] = None,
    client_card_data: Optional[Dict] = None,
) -> Optional[Dict[str, str]]:
    """
    Generate a single coaching tip for the current moment.

    Returns ``{"tip": str, "category": str}`` or ``None``.
    Categories: ``suggestion``, ``warning``, ``transition``, ``info``.
    """
    if len(conversation_text.strip()) < 100:
        return None

    # Build context
    pending_items = []
    if current_stage and checklist_progress is not None:
        for item in current_stage.get("items", []):
            if not checklist_progress.get(item["id"], False):
                pending_items.append(item["content"])

    pre_call_summary = ""
    if pre_call_data:
        parts = []
        for k, v in pre_call_data.items():
            if v:
                parts.append(f"- {k}: {v}")
        if parts:
            pre_call_summary = "\n".join(parts)

    client_summary = ""
    if client_card_data:
        parts = []
        for fid, fdata in client_card_data.items():
            val = fdata.get("value", "") if isinstance(fdata, dict) else str(fdata)
            if val:
                parts.append(f"- {fid}: {val}")
        if parts:
            client_summary = "\n".join(parts)

    prompt = f"""You are a real-time sales coach for a trial class call in Bahasa Indonesia.

Current stage: {current_stage.get('name', 'Unknown') if current_stage else 'Unknown'}

Pending checklist items:
{chr(10).join(f'- {p}' for p in pending_items) if pending_items else '(all done)'}

Pre-call briefing:
{pre_call_summary or '(none)'}

Client info extracted so far:
{client_summary or '(none)'}

Recent conversation:
{conversation_text[-500:]}

Generate ONE short, actionable coaching tip (max 2 sentences).
Focus on the most impactful thing the rep should do right now.

Return JSON: {{"tip": "...", "category": "suggestion|warning|transition|info"}}
"""

    llm = get_llm_client()
    try:
        raw = llm.call(prompt, temperature=0.4, max_tokens=150)
        result = json.loads(raw)
        if "error" in result:
            return None
        tip = result.get("tip", "")
        category = result.get("category", "suggestion")
        if tip and len(tip) > 5:
            return {"tip": tip, "category": category}
    except Exception:
        logger.debug("Coaching tip generation failed", exc_info=True)

    return None
