from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import OrganizationResponse, TeamResponse

router = APIRouter()


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(user: dict = Depends(get_current_user)):
    """Get the current user's organization."""
    supabase = get_supabase_client()
    result = (
        supabase.table("organizations")
        .select("*")
        .eq("id", user["organization_id"])
        .single()
        .execute()
    )
    return result.data


@router.get("/me/teams", response_model=list[TeamResponse])
async def get_organization_teams(user: dict = Depends(get_current_user)):
    """Get teams in the current user's organization."""
    supabase = get_supabase_client()
    result = (
        supabase.table("teams")
        .select("*")
        .eq("organization_id", user["organization_id"])
        .execute()
    )
    return result.data or []
