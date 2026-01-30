from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import (
    PlaybookResponse,
    PlaybookCreate,
    PlaybookUpdate,
    PlaybookVersionResponse,
    PlaybookVersionCreate,
)

router = APIRouter()


def _check_lead_or_admin(user: dict):
    if user.get("role") not in ("admin", "team_lead"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and team leads can manage playbooks",
        )


@router.get("", response_model=list[PlaybookResponse])
async def list_playbooks(user: dict = Depends(get_current_user)):
    """List playbooks for the user's organization."""
    supabase = get_supabase_client()
    result = (
        supabase.table("playbooks")
        .select("*")
        .eq("organization_id", user["organization_id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.post("", response_model=PlaybookResponse, status_code=201)
async def create_playbook(
    data: PlaybookCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new playbook."""
    _check_lead_or_admin(user)
    supabase = get_supabase_client()

    payload = {
        "organization_id": user["organization_id"],
        "name": data.name,
        "description": data.description,
        "team_id": data.team_id,
        "is_active": True,
        "created_by": user["id"],
    }

    result = supabase.table("playbooks").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create playbook")
    return result.data[0]


@router.get("/{playbook_id}", response_model=PlaybookResponse)
async def get_playbook(
    playbook_id: str,
    user: dict = Depends(get_current_user),
):
    """Get a single playbook."""
    supabase = get_supabase_client()
    result = (
        supabase.table("playbooks")
        .select("*")
        .eq("id", playbook_id)
        .eq("organization_id", user["organization_id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return result.data


@router.put("/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    playbook_id: str,
    data: PlaybookUpdate,
    user: dict = Depends(get_current_user),
):
    """Update a playbook."""
    _check_lead_or_admin(user)
    supabase = get_supabase_client()

    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        supabase.table("playbooks")
        .update(update_data)
        .eq("id", playbook_id)
        .eq("organization_id", user["organization_id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return result.data[0]


@router.delete("/{playbook_id}", status_code=204)
async def delete_playbook(
    playbook_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a playbook."""
    _check_lead_or_admin(user)
    supabase = get_supabase_client()
    supabase.table("playbooks").delete().eq("id", playbook_id).eq(
        "organization_id", user["organization_id"]
    ).execute()


# --- Versions ---


@router.get("/{playbook_id}/versions", response_model=list[PlaybookVersionResponse])
async def list_versions(
    playbook_id: str,
    user: dict = Depends(get_current_user),
):
    """List versions of a playbook."""
    supabase = get_supabase_client()
    # Verify playbook access
    pb = (
        supabase.table("playbooks")
        .select("id")
        .eq("id", playbook_id)
        .eq("organization_id", user["organization_id"])
        .single()
        .execute()
    )
    if not pb.data:
        raise HTTPException(status_code=404, detail="Playbook not found")

    result = (
        supabase.table("playbook_versions")
        .select("*")
        .eq("playbook_id", playbook_id)
        .order("version_number", desc=True)
        .execute()
    )
    return result.data or []


@router.post(
    "/{playbook_id}/versions",
    response_model=PlaybookVersionResponse,
    status_code=201,
)
async def create_version(
    playbook_id: str,
    data: PlaybookVersionCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new version of a playbook."""
    _check_lead_or_admin(user)
    supabase = get_supabase_client()

    # Get latest version number
    latest = (
        supabase.table("playbook_versions")
        .select("version_number")
        .eq("playbook_id", playbook_id)
        .order("version_number", desc=True)
        .limit(1)
        .execute()
    )
    next_version = (latest.data[0]["version_number"] + 1) if latest.data else 1

    payload = {
        "playbook_id": playbook_id,
        "version_number": next_version,
        "created_by": user["id"],
        **data.model_dump(exclude_none=True),
    }

    result = supabase.table("playbook_versions").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create version")
    return result.data[0]


@router.post("/{playbook_id}/versions/{version_id}/publish")
async def publish_version(
    playbook_id: str,
    version_id: str,
    user: dict = Depends(get_current_user),
):
    """Publish a playbook version."""
    _check_lead_or_admin(user)
    supabase = get_supabase_client()

    from datetime import datetime, timezone

    result = (
        supabase.table("playbook_versions")
        .update({"published_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", version_id)
        .eq("playbook_id", playbook_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"status": "published"}
