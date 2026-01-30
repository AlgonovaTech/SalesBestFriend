from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import (
    OverviewStatsResponse,
    UserScoreSummaryResponse,
    RadarDataPointResponse,
)

router = APIRouter()


@router.get("/overview", response_model=OverviewStatsResponse)
async def get_overview(user: dict = Depends(get_current_user)):
    """Get dashboard overview stats."""
    supabase = get_supabase_client()

    # Total calls for this user
    calls_query = supabase.table("calls").select("id, status, created_at")
    role = user.get("role")
    if role == "admin":
        calls_query = calls_query.eq("organization_id", user["organization_id"])
    elif role == "team_lead":
        calls_query = calls_query.eq("team_id", user["team_id"])
    else:
        calls_query = calls_query.eq("user_id", user["id"])

    calls_result = calls_query.execute()
    calls = calls_result.data or []

    total_calls = len(calls)
    completed_calls = [c for c in calls if c.get("status") == "completed"]

    # Calls this week
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    calls_this_week = len([
        c for c in completed_calls
        if c.get("created_at", "") >= week_ago
    ])

    # Get average score from analyses
    if completed_calls:
        call_ids = [c["id"] for c in completed_calls]
        analyses = (
            supabase.table("call_analyses")
            .select("overall_score")
            .in_("call_id", call_ids)
            .execute()
        )
        scores = [
            a["overall_score"]
            for a in (analyses.data or [])
            if a.get("overall_score") is not None
        ]
        average_score = sum(scores) / len(scores) if scores else 0.0
    else:
        average_score = 0.0

    # Score trend (compare this week vs previous week)
    two_weeks_ago = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    this_week_calls = [c for c in completed_calls if c.get("created_at", "") >= week_ago]
    prev_week_calls = [
        c for c in completed_calls
        if two_weeks_ago <= c.get("created_at", "") < week_ago
    ]

    score_trend = 0.0
    if this_week_calls and prev_week_calls:
        tw_ids = [c["id"] for c in this_week_calls]
        pw_ids = [c["id"] for c in prev_week_calls]

        tw_analyses = (
            supabase.table("call_analyses")
            .select("overall_score")
            .in_("call_id", tw_ids)
            .execute()
        )
        pw_analyses = (
            supabase.table("call_analyses")
            .select("overall_score")
            .in_("call_id", pw_ids)
            .execute()
        )

        tw_scores = [a["overall_score"] for a in (tw_analyses.data or []) if a.get("overall_score") is not None]
        pw_scores = [a["overall_score"] for a in (pw_analyses.data or []) if a.get("overall_score") is not None]

        if tw_scores and pw_scores:
            tw_avg = sum(tw_scores) / len(tw_scores)
            pw_avg = sum(pw_scores) / len(pw_scores)
            score_trend = round(tw_avg - pw_avg, 1)

    # Pending tasks
    tasks_result = (
        supabase.table("call_tasks")
        .select("id")
        .eq("user_id", user["id"])
        .eq("status", "pending")
        .execute()
    )
    total_tasks_pending = len(tasks_result.data or [])

    return OverviewStatsResponse(
        total_calls=total_calls,
        calls_this_week=calls_this_week,
        average_score=round(average_score, 1),
        score_trend=score_trend,
        total_tasks_pending=total_tasks_pending,
    )


@router.get("/team", response_model=list[UserScoreSummaryResponse])
async def get_team_analytics(user: dict = Depends(get_current_user)):
    """Get team performance analytics (admin/lead only)."""
    if user.get("role") not in ("admin", "team_lead"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    supabase = get_supabase_client()

    # Get team members
    if user.get("role") == "admin":
        members_result = (
            supabase.table("user_profiles")
            .select("*")
            .eq("organization_id", user["organization_id"])
            .execute()
        )
    else:
        members_result = (
            supabase.table("user_profiles")
            .select("*")
            .eq("team_id", user["team_id"])
            .execute()
        )

    members = members_result.data or []
    summaries = []

    for member in members:
        calls = (
            supabase.table("calls")
            .select("id")
            .eq("user_id", member["id"])
            .eq("status", "completed")
            .execute()
        )
        call_ids = [c["id"] for c in (calls.data or [])]

        avg_score = 0.0
        if call_ids:
            analyses = (
                supabase.table("call_analyses")
                .select("overall_score")
                .in_("call_id", call_ids)
                .execute()
            )
            scores = [
                a["overall_score"]
                for a in (analyses.data or [])
                if a.get("overall_score") is not None
            ]
            avg_score = sum(scores) / len(scores) if scores else 0.0

        summaries.append(
            UserScoreSummaryResponse(
                user_id=member["id"],
                full_name=member.get("full_name", ""),
                avatar_url=member.get("avatar_url"),
                total_calls=len(call_ids),
                average_score=round(avg_score, 1),
            )
        )

    return summaries


@router.get("/radar/{user_id}", response_model=list[RadarDataPointResponse])
async def get_radar_data(
    user_id: str,
    user: dict = Depends(get_current_user),
):
    """Get radar chart data for a user."""
    supabase = get_supabase_client()

    # Get scores grouped by criteria
    calls = (
        supabase.table("calls")
        .select("id")
        .eq("user_id", user_id)
        .eq("status", "completed")
        .execute()
    )
    call_ids = [c["id"] for c in (calls.data or [])]

    if not call_ids:
        return []

    scores = (
        supabase.table("call_scores")
        .select("criteria_name, criteria_max_score, score")
        .in_("call_id", call_ids)
        .execute()
    )

    # Aggregate by criteria
    criteria_scores: dict[str, dict] = {}
    for s in scores.data or []:
        name = s["criteria_name"]
        if name not in criteria_scores:
            criteria_scores[name] = {
                "total": 0,
                "count": 0,
                "max": s["criteria_max_score"],
            }
        criteria_scores[name]["total"] += s["score"]
        criteria_scores[name]["count"] += 1

    return [
        RadarDataPointResponse(
            criteria=name,
            score=round(data["total"] / data["count"], 1) if data["count"] else 0,
            max=data["max"],
        )
        for name, data in criteria_scores.items()
    ]
