"""
Post-call analysis service.
Generates summary, scores, action items, and buyer profile
from the full call transcript.
"""

import json
import logging
from typing import Dict, List, Optional

from app.services.llm.base import get_llm_client
from app.config import get_settings

logger = logging.getLogger(__name__)


def analyze_call(
    transcript: str,
    scoring_criteria: Optional[List[Dict]] = None,
    playbook_guidelines: Optional[str] = None,
) -> Dict:
    """
    Run post-call analysis on the full transcript.

    Returns::

        {
            "summary": str,
            "what_went_well": [str, ...],
            "needs_improvement": [str, ...],
            "goals_identified": [str, ...],
            "pain_points": [str, ...],
            "interest_signals": [str, ...],
            "buyer_profile_summary": str,
            "overall_score": float,
            "criteria_scores": [{"name", "score", "max_score", "reasoning", "evidence"}, ...],
            "action_items": [{"title", "priority"}, ...],
        }
    """
    settings = get_settings()
    llm = get_llm_client()
    model = settings.llm_analysis_model  # Use Claude for deeper analysis

    # Build scoring section
    criteria_block = ""
    if scoring_criteria:
        lines = []
        for c in scoring_criteria:
            lines.append(
                f"- {c['name']} (max {c.get('max_score', 10)}): {c.get('description', '')}"
            )
        criteria_block = "\n".join(lines)

    guidelines_block = ""
    if playbook_guidelines:
        guidelines_block = f"\nMethodology guidelines:\n{playbook_guidelines[:2000]}"

    prompt = f"""You are an expert sales call analyst.

FULL TRANSCRIPT (may be in Bahasa Indonesia):
{transcript[:8000]}

{guidelines_block}

SCORING CRITERIA:
{criteria_block or "(use general sales best practices)"}

Analyze this call thoroughly. Provide:

1. A concise summary (2-3 sentences)
2. What went well (3-5 bullet points)
3. What needs improvement (3-5 bullet points)
4. Client goals identified
5. Client pain points
6. Interest signals (buying cues)
7. Brief buyer profile summary
8. Overall score (0-100)
9. Per-criteria scores (if criteria provided)
10. Actionable follow-up items (2-4 tasks with priority: high/medium/low)

Return ONLY valid JSON:
{{
  "summary": "...",
  "what_went_well": ["..."],
  "needs_improvement": ["..."],
  "goals_identified": ["..."],
  "pain_points": ["..."],
  "interest_signals": ["..."],
  "buyer_profile_summary": "...",
  "overall_score": 0.0,
  "criteria_scores": [
    {{"name": "...", "score": 0, "max_score": 10, "reasoning": "...", "evidence": "..."}}
  ],
  "action_items": [
    {{"title": "...", "priority": "high|medium|low"}}
  ]
}}
"""

    try:
        raw = llm.call(prompt, temperature=0.3, max_tokens=2000, model=model)
        result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(result.get("details", "API error"))
        return result
    except Exception:
        logger.exception("Post-call analysis failed")
        return {
            "summary": "Analysis failed. Please try again.",
            "what_went_well": [],
            "needs_improvement": [],
            "goals_identified": [],
            "pain_points": [],
            "interest_signals": [],
            "buyer_profile_summary": "",
            "overall_score": 0.0,
            "criteria_scores": [],
            "action_items": [],
        }
