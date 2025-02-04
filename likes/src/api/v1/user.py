from core.config import settings
from fastapi import APIRouter, Depends, Query, Request
from fastapi_cache.decorator import cache
from schemas.responses import UserResponse
from services.auth import PermService, get_perm_service
from services.like import LikeService, get_like_service

router = APIRouter()


@router.get("/", response_model=UserResponse)
@cache(expire=settings.cache_expire_in_seconds)
async def get_user(
    request: Request,
    like_service: LikeService = Depends(get_like_service),
    auth_service: PermService = Depends(get_perm_service),
    access_token: str = Query(..., description="Access token of the user"),
) -> dict:
    """
    Retrieve user details by token.
    """
    user_id = await auth_service.is_validuser(request, access_token)
    user_info = await like_service.get_user_info(user_id)
    return user_info
