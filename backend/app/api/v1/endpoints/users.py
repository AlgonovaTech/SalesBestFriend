from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import get_current_user
from app.models.database import get_supabase_client
from app.models.schemas import UserProfileResponse, UserProfileUpdate

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_profile(user: dict = Depends(get_current_user)):
    """Get the current user's profile."""
    return user


@router.put("/me", response_model=UserProfileResponse)
async def update_current_profile(
    data: UserProfileUpdate,
    user: dict = Depends(get_current_user),
):
    """Update the current user's profile."""
    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        return user

    supabase = get_supabase_client()
    result = (
        supabase.table("user_profiles")
        .update(update_data)
        .eq("id", user["id"])
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update profile")

    return result.data[0]


@router.get("", response_model=list[UserProfileResponse])
async def list_users(user: dict = Depends(get_current_user)):
    """List users visible to the current user based on role."""
    supabase = get_supabase_client()
    role = user.get("role")

    query = supabase.table("user_profiles").select("*")

    if role == "admin":
        query = query.eq("organization_id", user["organization_id"])
    elif role == "team_lead":
        query = query.eq("team_id", user["team_id"])
    else:
        query = query.eq("id", user["id"])

    result = query.execute()
    return result.data or []
