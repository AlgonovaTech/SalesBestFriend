from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import TagResponse, TagCreate

router = APIRouter()


@router.get("", response_model=list[TagResponse])
async def list_tags(user: dict = Depends(get_current_user)):
    """List tags for the user's organization."""
    supabase = get_supabase_client()
    result = (
        supabase.table("tags")
        .select("*")
        .eq("organization_id", user["organization_id"])
        .order("name")
        .execute()
    )
    return result.data or []


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    user: dict = Depends(get_current_user),
):
    """Create a tag (admin/lead only)."""
    if user.get("role") not in ("admin", "team_lead"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    supabase = get_supabase_client()
    payload = {
        "organization_id": user["organization_id"],
        "name": data.name,
        "color": data.color,
    }
    result = supabase.table("tags").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create tag")
    return result.data[0]


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a tag (admin/lead only)."""
    if user.get("role") not in ("admin", "team_lead"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    supabase = get_supabase_client()
    supabase.table("tags").delete().eq("id", tag_id).eq(
        "organization_id", user["organization_id"]
    ).execute()
