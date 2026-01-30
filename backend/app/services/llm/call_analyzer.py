"""
Post-call analysis service.
Generates summary, scores, action items, and buyer profile
from the full call transcript.

Supports two modes:
1. Simple analysis (no playbook documents) — general sales analysis
2. TCM QC analysis (with playbook documents) — detailed criteria evaluation
"""

import json
import logging
from typing import Dict, List, Optional

from app.services.llm.base import get_llm_client
from app.config import get_settings

logger = logging.getLogger(__name__)

# Maximum transcript chars to send
MAX_TRANSCRIPT_CHARS = 40_000
# Maximum analysis documents chars (condensed to fit within model limits)
MAX_DOCS_CHARS = 40_000


def analyze_call(
    transcript: str,
    scoring_criteria: Optional[List[Dict]] = None,
    playbook_guidelines: Optional[str] = None,
) -> Dict:
    """
    Run post-call analysis on the full transcript.

    If playbook_guidelines contains '--- Analysis Documents ---',
    uses TCM QC mode with full criteria prompts.

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
    # Determine if we have TCM QC documents
    has_analysis_docs = (
        playbook_guidelines
        and "--- Analysis Documents ---" in playbook_guidelines
    )

    if has_analysis_docs:
        return _analyze_tcm_qc(transcript, scoring_criteria, playbook_guidelines)
    else:
        return _analyze_simple(transcript, scoring_criteria, playbook_guidelines)


def _analyze_simple(
    transcript: str,
    scoring_criteria: Optional[List[Dict]] = None,
    playbook_guidelines: Optional[str] = None,
) -> Dict:
    """Simple analysis without detailed criteria documents."""
    settings = get_settings()
    llm = get_llm_client()
    model = settings.llm_analysis_model

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
        guidelines_block = f"\nMethodology guidelines:\n{playbook_guidelines[:4000]}"

    prompt = f"""You are an expert sales call analyst.

FULL TRANSCRIPT (may be in Bahasa Indonesia):
{transcript[:MAX_TRANSCRIPT_CHARS]}

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
        raw = llm.call(prompt, temperature=0.3, max_tokens=4000, model=model)
        result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(result.get("details", "API error"))
        return result
    except Exception:
        logger.exception("Simple post-call analysis failed")
        return _empty_result()


def _analyze_tcm_qc(
    transcript: str,
    scoring_criteria: Optional[List[Dict]] = None,
    playbook_guidelines: Optional[str] = None,
) -> Dict:
    """
    TCM QC analysis with full criteria evaluation.
    Uses the analysis documents (individual criterion prompts) from playbook.
    """
    settings = get_settings()
    llm = get_llm_client()
    model = settings.llm_analysis_model

    # Split guidelines and analysis documents
    parts = playbook_guidelines.split("--- Analysis Documents ---")
    guidelines_text = parts[0].strip()
    docs_text = parts[1].strip() if len(parts) > 1 else ""

    # Truncate transcript if too long but keep as much as possible
    transcript_text = transcript[:MAX_TRANSCRIPT_CHARS]
    docs_text = docs_text[:MAX_DOCS_CHARS]

    prompt = f"""You are an expert QC analyst for Algonova (EdTech company in Indonesia).
You are evaluating a Trial Class Master (TCM) sales call.

{guidelines_text}

=== FULL CALL TRANSCRIPT ===
{transcript_text}
=== END TRANSCRIPT ===

=== EVALUATION CRITERIA AND PROMPTS ===
Below are the detailed criteria. For each criterion, follow the specific prompt instructions.
Score each criterion as described (usually [1], [0], or [Empty]).

{docs_text}
=== END CRITERIA ===

IMPORTANT INSTRUCTIONS:
1. Evaluate EVERY criterion listed above
2. For each criterion, provide the score AND detailed reasons with direct quotes from the transcript
3. Reasons MUST include quotes in the original language (Indonesian)
4. Calculate the overall score as: (sum of [1] scores / total scoreable criteria) * 100
5. For criterion 38 (Talk ratio), calculate the percentage
6. For criterion 39 (Sales methodologies), provide sum score 0-50
7. For criteria 42-46, score as [Advice] and provide detailed recommendations
8. Also provide a general summary, what went well, what needs improvement

Return ONLY valid JSON with this structure:
{{
  "summary": "2-3 sentence call summary",
  "what_went_well": ["point 1", "point 2", "point 3"],
  "needs_improvement": ["point 1", "point 2", "point 3"],
  "goals_identified": ["goal 1", "goal 2"],
  "pain_points": ["pain 1", "pain 2"],
  "interest_signals": ["signal 1", "signal 2"],
  "buyer_profile_summary": "Brief parent and child profile",
  "overall_score": 65.0,
  "criteria_scores": [
    {{
      "name": "1. Greeting and introduction",
      "score": 1,
      "max_score": 1,
      "reasoning": "Detailed reasoning with quotes...",
      "evidence": "Direct quote from transcript in Indonesian"
    }}
  ],
  "action_items": [
    {{"title": "Follow up with parent about payment", "priority": "high"}}
  ]
}}

Make sure criteria_scores includes ALL criteria (1-49). Return ONLY valid JSON, no other text."""

    try:
        raw = llm.call(prompt, temperature=0.2, max_tokens=16000, model=model)
        result = json.loads(raw)
        if "error" in result:
            raise RuntimeError(result.get("details", "API error"))

        # Ensure overall_score is reasonable
        if isinstance(result.get("overall_score"), (int, float)):
            result["overall_score"] = min(100.0, max(0.0, float(result["overall_score"])))

        return result
    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM JSON response: %s", e)
        logger.error("Raw response (first 500 chars): %s", raw[:500] if raw else "empty")
        return _empty_result("Analysis completed but response parsing failed.")
    except Exception:
        logger.exception("TCM QC analysis failed")
        return _empty_result()


def _empty_result(summary: str = "Analysis failed. Please try again.") -> Dict:
    """Return empty analysis result."""
    return {
        "summary": summary,
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
