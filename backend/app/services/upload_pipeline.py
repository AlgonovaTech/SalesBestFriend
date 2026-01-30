"""
Upload processing pipeline for call files and YouTube URLs.

Flow:
  1. [downloading]  — yt-dlp (YouTube only) or read uploaded file
  2. [transcribing] — Groq Whisper API
  3. [analyzing]    — Claude via OpenRouter + playbook documents
  4. Store: transcript, analysis, scores, tasks
  5. status → completed
"""

import logging
import os
import subprocess
import tempfile
from typing import Optional

from app.models.database import get_supabase_client
from app.services.transcription import transcribe_audio_buffer
from app.services.llm.call_analyzer import analyze_call

logger = logging.getLogger(__name__)


def _update_call(call_id: str, **fields):
    supabase = get_supabase_client()
    supabase.table("calls").update(fields).eq("id", call_id).execute()


def _set_step(call_id: str, step: str):
    _update_call(call_id, processing_step=step)


def _get_playbook_context(call_id: str) -> tuple[Optional[str], Optional[list], Optional[str]]:
    """Fetch playbook guidelines, scoring criteria, and analysis documents for a call."""
    supabase = get_supabase_client()

    call = supabase.table("calls").select("playbook_version_id, team_id").eq("id", call_id).single().execute()
    if not call.data or not call.data.get("playbook_version_id"):
        return None, None, None

    version_id = call.data["playbook_version_id"]
    version = (
        supabase.table("playbook_versions")
        .select("playbook_id, guidelines_content, scoring_criteria")
        .eq("id", version_id)
        .single()
        .execute()
    )
    if not version.data:
        return None, None, None

    guidelines = version.data.get("guidelines_content")
    scoring = version.data.get("scoring_criteria")
    playbook_id = version.data.get("playbook_id")

    # Fetch analysis documents for this playbook
    analysis_docs_content = None
    if playbook_id:
        docs_result = (
            supabase.table("playbook_documents")
            .select("title, content")
            .eq("playbook_id", playbook_id)
            .eq("document_type", "analysis")
            .order("sort_order")
            .execute()
        )
        if docs_result.data:
            parts = []
            for doc in docs_result.data:
                parts.append(f"### {doc['title']}\n{doc['content']}")
            analysis_docs_content = "\n\n".join(parts)

    return guidelines, scoring, analysis_docs_content


def _store_results(call_id: str, user_id: str, analysis: dict):
    """Store analysis, scores, and tasks in Supabase."""
    supabase = get_supabase_client()

    # Store analysis
    analysis_payload = {
        "call_id": call_id,
        "summary": analysis.get("summary", ""),
        "what_went_well": analysis.get("what_went_well", []),
        "needs_improvement": analysis.get("needs_improvement", []),
        "goals_identified": analysis.get("goals_identified", []),
        "pain_points": analysis.get("pain_points", []),
        "interest_signals": analysis.get("interest_signals", []),
        "buyer_profile_summary": analysis.get("buyer_profile_summary", ""),
        "overall_score": analysis.get("overall_score", 0),
        "model_used": "claude-via-openrouter",
    }
    supabase.table("call_analyses").insert(analysis_payload).execute()

    # Store scores
    for cs in analysis.get("criteria_scores", []):
        score_payload = {
            "call_id": call_id,
            "criteria_name": cs.get("name", ""),
            "criteria_max_score": cs.get("max_score", 10),
            "score": cs.get("score", 0),
            "reasoning": cs.get("reasoning", ""),
            "evidence": cs.get("evidence", ""),
        }
        supabase.table("call_scores").insert(score_payload).execute()

    # Store tasks
    for item in analysis.get("action_items", []):
        task_payload = {
            "call_id": call_id,
            "user_id": user_id,
            "title": item.get("title", ""),
            "status": "pending",
            "priority": item.get("priority", "medium"),
        }
        supabase.table("call_tasks").insert(task_payload).execute()


async def _transcribe_file(file_path: str, language: str) -> str:
    """Read file and transcribe via the transcription service."""
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    segments = await transcribe_audio_buffer(audio_bytes, language)
    return "\n".join(s["text"] for s in segments)


def _download_youtube(url: str, output_dir: str) -> str:
    """Download audio from YouTube URL using yt-dlp. Returns path to audio file."""
    output_path = os.path.join(output_dir, "audio.%(ext)s")
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "wav",
        "--audio-quality", "0",
        "--no-playlist",
        "--output", output_path,
        url,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=300)

    # Find the output file
    for fname in os.listdir(output_dir):
        if fname.startswith("audio"):
            return os.path.join(output_dir, fname)

    raise FileNotFoundError("yt-dlp did not produce an audio file")


async def process_uploaded_call(
    call_id: str,
    user_id: str,
    file_path: str,
    language: str = "en",
):
    """Process an uploaded audio/video file through the full pipeline."""
    try:
        _update_call(call_id, status="processing")

        # Step 1: Transcribe
        _set_step(call_id, "transcribing")
        transcript_text = await _transcribe_file(file_path, language)

        if not transcript_text.strip():
            _update_call(call_id, status="failed", processing_step="failed:no_transcript")
            return

        # Store transcript segments
        supabase = get_supabase_client()
        for i, line in enumerate(transcript_text.split("\n")):
            if line.strip():
                supabase.table("call_transcripts").insert({
                    "call_id": call_id,
                    "segment_index": i,
                    "start_seconds": 0,
                    "end_seconds": 0,
                    "text": line.strip(),
                    "speaker": "speaker",
                    "confidence": 0.9,
                }).execute()

        # Step 2: Analyze
        _set_step(call_id, "analyzing")
        guidelines, scoring, analysis_docs = _get_playbook_context(call_id)

        # Build enhanced prompt with analysis documents
        enhanced_guidelines = guidelines or ""
        if analysis_docs:
            enhanced_guidelines += f"\n\n--- Analysis Documents ---\n{analysis_docs}"

        analysis = analyze_call(
            transcript=transcript_text,
            scoring_criteria=scoring,
            playbook_guidelines=enhanced_guidelines if enhanced_guidelines else None,
        )

        # Step 3: Store results
        _set_step(call_id, "storing")
        _store_results(call_id, user_id, analysis)

        # Done
        _update_call(call_id, status="completed", processing_step="done")

    except Exception:
        logger.exception("Upload pipeline failed for call %s", call_id)
        _update_call(call_id, status="failed", processing_step="failed:error")
    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)


async def process_youtube_call(
    call_id: str,
    user_id: str,
    youtube_url: str,
    language: str = "en",
):
    """Process a YouTube URL through download → transcribe → analyze pipeline."""
    tmp_dir = None
    try:
        _update_call(call_id, status="processing")

        # Step 1: Download
        _set_step(call_id, "downloading")
        tmp_dir = tempfile.mkdtemp(prefix="sbf_yt_")
        audio_path = _download_youtube(youtube_url, tmp_dir)

        # Step 2: Transcribe
        _set_step(call_id, "transcribing")
        transcript_text = await _transcribe_file(audio_path, language)

        if not transcript_text.strip():
            _update_call(call_id, status="failed", processing_step="failed:no_transcript")
            return

        # Store transcript
        supabase = get_supabase_client()
        for i, line in enumerate(transcript_text.split("\n")):
            if line.strip():
                supabase.table("call_transcripts").insert({
                    "call_id": call_id,
                    "segment_index": i,
                    "start_seconds": 0,
                    "end_seconds": 0,
                    "text": line.strip(),
                    "speaker": "speaker",
                    "confidence": 0.9,
                }).execute()

        # Step 3: Analyze
        _set_step(call_id, "analyzing")
        guidelines, scoring, analysis_docs = _get_playbook_context(call_id)

        enhanced_guidelines = guidelines or ""
        if analysis_docs:
            enhanced_guidelines += f"\n\n--- Analysis Documents ---\n{analysis_docs}"

        analysis = analyze_call(
            transcript=transcript_text,
            scoring_criteria=scoring,
            playbook_guidelines=enhanced_guidelines if enhanced_guidelines else None,
        )

        # Step 4: Store results
        _set_step(call_id, "storing")
        _store_results(call_id, user_id, analysis)

        # Done
        _update_call(call_id, status="completed", processing_step="done")

    except Exception:
        logger.exception("YouTube pipeline failed for call %s", call_id)
        _update_call(call_id, status="failed", processing_step="failed:error")
    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
