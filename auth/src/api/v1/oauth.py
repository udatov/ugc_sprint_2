from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from services.oauth import get_oauthprovider_service

router = APIRouter()


@router.get("/{oauth_provider}")
async def auth_provider(oauth_provider: str) -> RedirectResponse:
    """
    Redirect to OAuth Provider authorization page.

    **Endpoint**: GET `/{oauth_provider}`

    :return: A redirect response to the OAuth Provider authorization URL.
    :raises HTTPException: If the requested OAuth provider is not supported.
    """
    service = get_oauthprovider_service(oauth_provider)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found."
        )

    return RedirectResponse(url=service.auth_url)


@router.get("/{oauth_provider}/callback")
async def auth_provider_callback(
    request: Request, oauth_provider: str, code: str
) -> dict[str, Any]:
    """
    Handle the OAuth callback and retrieve the access token.

    **Endpoint**: GET `/{oauth_provider}/callback`

    :param request: The FastAPI Request object used for rate-limiting.
    :param code: The authorization code received from OAuth.
    :return: A dictionary containing the access token and user info.
    :raises HTTPException: If the access token cannot be retrieved or if
                          user info cannot be found.
    """
    service = get_oauthprovider_service(oauth_provider)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider service not available.",
        )
    access_token = await service.get_access_token(request, code)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to retrieve access token. Check the provided code.",
        )

    user_info = await service.get_user_info(request, access_token)

    return {"oauth_access_token": access_token, "user_info": user_info}
