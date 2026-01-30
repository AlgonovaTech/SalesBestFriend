import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, BackgroundTasks
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import (
    CallResponse,
    CallCreate,
    CallUpdate,
    TranscriptSegmentResponse,
    CallAnalysisResponse,
    CallScoreResponse,
    CallTaskResponse,
    CallTaskCreate,
    CallTaskUpdate,
    PaginatedResponse,
    YouTubeUploadRequest,
)
from app.services.upload_pipeline import process_uploaded_call, process_youtube_call

router = APIRouter()


def _call_query_for_user(supabase, user: dict):
    """Build a call query filtered by user role."""
    query = supabase.table("calls").select("*")
    role = user.get("role")

    if role == "admin":
        query = query.eq("organization_id", user["organization_id"])
    elif role == "team_lead":
        query = query.eq("team_id", user["team_id"])
    else:
        query = query.eq("user_id", user["id"])

    return query


@router.get("", response_model=PaginatedResponse)
async def list_calls(
    user: dict = Depends(get_current_user),
    status: str | None = None,
    source: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List calls with filters and pagination."""
    supabase = get_supabase_client()
    query = _call_query_for_user(supabase, user)

    if status:
        query = query.eq("status", status)
    if source:
        query = query.eq("source", source)
    if search:
        query = query.ilike("title", f"%{search}%")

    # Count total
    count_query = _call_query_for_user(supabase, user)
    if status:
        count_query = count_query.eq("status", status)
    if source:
        count_query = count_query.eq("source", source)
    if search:
        count_query = count_query.ilike("title", f"%{search}%")

    count_result = count_query.execute()
    total = len(count_result.data) if count_result.data else 0

    # Paginate
    offset = (page - 1) * per_page
    result = (
        query.order("created_at", desc=True)
        .range(offset, offset + per_page - 1)
        .execute()
    )

    return PaginatedResponse(
        data=result.data or [],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.post("", response_model=CallResponse, status_code=201)
async def create_call(
    data: CallCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new call."""
    supabase = get_supabase_client()

    payload = {
        "organization_id": user["organization_id"],
        "team_id": user["team_id"],
        "user_id": user["id"],
        "title": data.title,
        "status": "scheduled",
        "source": data.source.value,
        "language": data.language,
        "playbook_version_id": data.playbook_version_id,
        "pre_call_data": data.pre_call_data,
    }

    result = supabase.table("calls").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create call")
    return result.data[0]


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    user: dict = Depends(get_current_user),
):
    """Get a single call."""
    supabase = get_supabase_client()
    query = _call_query_for_user(supabase, user)
    result = query.eq("id", call_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Call not found")
    return result.data


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    data: CallUpdate,
    user: dict = Depends(get_current_user),
):
    """Update a call."""
    supabase = get_supabase_client()
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Verify access
    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    result = (
        supabase.table("calls").update(update_data).eq("id", call_id).execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update call")
    return result.data[0]


@router.delete("/{call_id}", status_code=204)
async def delete_call(
    call_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a call (owner only)."""
    supabase = get_supabase_client()
    supabase.table("calls").delete().eq("id", call_id).eq(
        "user_id", user["id"]
    ).execute()


# --- Transcript ---


@router.get("/{call_id}/transcript", response_model=list[TranscriptSegmentResponse])
async def get_transcript(
    call_id: str,
    user: dict = Depends(get_current_user),
):
    """Get transcript segments for a call."""
    supabase = get_supabase_client()

    # Verify access
    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    result = (
        supabase.table("call_transcripts")
        .select("*")
        .eq("call_id", call_id)
        .order("segment_index")
        .execute()
    )
    return result.data or []


# --- Analysis ---


@router.get("/{call_id}/analysis", response_model=CallAnalysisResponse)
async def get_analysis(
    call_id: str,
    user: dict = Depends(get_current_user),
):
    """Get AI analysis for a call."""
    supabase = get_supabase_client()

    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    result = (
        supabase.table("call_analyses")
        .select("*")
        .eq("call_id", call_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result.data


@router.post("/{call_id}/analyze")
async def trigger_analysis(
    call_id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Trigger post-call AI analysis on an existing call with transcript."""
    supabase = get_supabase_client()

    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    # Get transcript
    transcript_result = (
        supabase.table("call_transcripts")
        .select("text")
        .eq("call_id", call_id)
        .order("segment_index")
        .execute()
    )
    if not transcript_result.data:
        raise HTTPException(status_code=400, detail="No transcript found for this call")

    transcript_text = "\n".join(seg["text"] for seg in transcript_result.data)

    # Run analysis in background
    from app.services.upload_pipeline import _get_playbook_context, _store_results, _update_call, _set_step
    from app.services.llm.call_analyzer import analyze_call as run_analysis

    def _run_analysis():
        try:
            _update_call(call_id, status="processing")
            _set_step(call_id, "analyzing")

            guidelines, scoring, analysis_docs = _get_playbook_context(call_id)
            enhanced_guidelines = guidelines or ""
            if analysis_docs:
                enhanced_guidelines += f"\n\n--- Analysis Documents ---\n{analysis_docs}"

            analysis = run_analysis(
                transcript=transcript_text,
                scoring_criteria=scoring,
                playbook_guidelines=enhanced_guidelines if enhanced_guidelines else None,
            )
            _set_step(call_id, "storing")
            _store_results(call_id, user["id"], analysis)
            _update_call(call_id, status="completed", processing_step="done")
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Analysis failed for call %s", call_id)
            _update_call(call_id, status="failed", processing_step="failed:analysis_error")

    background_tasks.add_task(_run_analysis)

    return {"status": "processing", "call_id": call_id}


# --- Upload ---


@router.post("/upload", response_model=CallResponse, status_code=201)
async def upload_call(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(""),
    language: str = Form("en"),
    playbook_version_id: str = Form(""),
    user: dict = Depends(get_current_user),
):
    """Upload an audio/video file for post-analysis."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Save to temp file
    suffix = os.path.splitext(file.filename)[1] or ".wav"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="sbf_upload_")
    content = await file.read()
    tmp.write(content)
    tmp.close()

    # Create call record
    supabase = get_supabase_client()
    call_title = title or file.filename or "Uploaded Call"
    payload = {
        "organization_id": user["organization_id"],
        "team_id": user["team_id"],
        "user_id": user["id"],
        "title": call_title,
        "status": "processing",
        "source": "upload",
        "language": language,
        "playbook_version_id": playbook_version_id or None,
        "audio_storage_path": tmp.name,
        "processing_step": "queued",
    }
    result = supabase.table("calls").insert(payload).execute()
    if not result.data:
        os.remove(tmp.name)
        raise HTTPException(status_code=500, detail="Failed to create call")

    call_data = result.data[0]

    # Process in background
    background_tasks.add_task(
        process_uploaded_call,
        call_id=call_data["id"],
        user_id=user["id"],
        file_path=tmp.name,
        language=language,
    )

    return call_data


@router.post("/upload-youtube", response_model=CallResponse, status_code=201)
async def upload_youtube(
    data: YouTubeUploadRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
):
    """Upload a YouTube URL for download, transcription, and analysis."""
    supabase = get_supabase_client()
    call_title = data.title or f"YouTube: {data.youtube_url[:50]}"

    payload = {
        "organization_id": user["organization_id"],
        "team_id": user["team_id"],
        "user_id": user["id"],
        "title": call_title,
        "status": "processing",
        "source": "upload",
        "language": data.language,
        "playbook_version_id": data.playbook_version_id,
        "youtube_url": data.youtube_url,
        "processing_step": "queued",
    }
    result = supabase.table("calls").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create call")

    call_data = result.data[0]

    # Process in background
    background_tasks.add_task(
        process_youtube_call,
        call_id=call_data["id"],
        user_id=user["id"],
        youtube_url=data.youtube_url,
        language=data.language,
    )

    return call_data


# --- Scores ---


@router.get("/{call_id}/scores", response_model=list[CallScoreResponse])
async def get_scores(
    call_id: str,
    user: dict = Depends(get_current_user),
):
    """Get score breakdown for a call."""
    supabase = get_supabase_client()

    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    result = (
        supabase.table("call_scores")
        .select("*")
        .eq("call_id", call_id)
        .execute()
    )
    return result.data or []


# --- Tasks ---


@router.get("/{call_id}/tasks", response_model=list[CallTaskResponse])
async def get_tasks(
    call_id: str,
    user: dict = Depends(get_current_user),
):
    """Get action items for a call."""
    supabase = get_supabase_client()

    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    result = (
        supabase.table("call_tasks")
        .select("*")
        .eq("call_id", call_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


@router.post("/{call_id}/tasks", response_model=CallTaskResponse, status_code=201)
async def create_task(
    call_id: str,
    data: CallTaskCreate,
    user: dict = Depends(get_current_user),
):
    """Create a task for a call."""
    supabase = get_supabase_client()

    existing = _call_query_for_user(supabase, user).eq("id", call_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Call not found")

    payload = {
        "call_id": call_id,
        "user_id": user["id"],
        "title": data.title,
        "status": "pending",
        "due_date": data.due_date,
        "priority": data.priority,
    }

    result = supabase.table("call_tasks").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create task")
    return result.data[0]
