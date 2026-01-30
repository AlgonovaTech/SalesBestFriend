import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings
from app.models.database import get_supabase_client

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate Supabase JWT and return user info.

    Uses Supabase's auth.getUser() with the access token, which is the
    most reliable method since it validates against Supabase directly.
    """
    token = credentials.credentials

    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user = user_response.user

        # Fetch profile from user_profiles table
        profile_response = (
            supabase.table("user_profiles")
            .select("*")
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found",
            )

        return profile_response.data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )


async def require_role(roles: list[str]):
    """Factory for role-based access control dependency."""

    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _check
