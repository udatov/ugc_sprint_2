import secrets

from core.config import settings
from db.basecache import get_cache
from db.basedb import get_session
from db.models.user import User
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from redis.asyncio import Redis
from schemas.user import (
    HistoryResponse,
    Signin,
    SigninResponse,
    Signup,
    SignupResponse,
    TokenResponse,
    UserWithRolesResponse,
)
from services.auth import get_current_user
from services.oauth import get_oauthprovider_service
from services.role import RoleService, get_role_service
from services.token import TokenService, get_token_service
from services.user import UserService, get_user_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/signup", response_model=SignupResponse)
async def signup(
    model: Signup,
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
    session: AsyncSession = Depends(get_session),
) -> SignupResponse:
    """
    Register a new user.

    **Endpoint**: POST `/signup`

    :param model: The user signup details.
    :param user_service: The user service to handle user operations.
    :param role_service: The role service to assign default roles to users.
    :param session: The database session.
    :return: The created user data.
    :raises HTTPException: If the user already exists.
    """
    user = await user_service.get_by_login(session, model.login)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists!"
        )

    user = await user_service.create_or_update(
        session, model.login, model.password, model.first_name, model.last_name
    )

    await role_service.assign_role(session, user.id, settings.default_role_uuid)

    return user


@router.post("/signin", response_model=SigninResponse)
async def signin(
    model: Signin,
    request: Request,
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
    role_service: RoleService = Depends(get_role_service),
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
) -> SigninResponse:
    """
    Authenticate a user and retrieve tokens along with user info.
    Using for siging:
    - login and possword or
    - Yandex access token - can be get from Endpoint /api/v1/oauth/yandex

    **Endpoint**: POST `/signin`

    :param model: The login credentials of the user.
    :param request: The FastAPI Request object used for rate-limiting.
    :param user_service: The user service to validate users.
    :param token_service: The token service to issue tokens.
    :param session: The database session.
    :param cache: The Redis cache to handle token storage.
    :return: Access and refresh tokens along with user info.
    :raises HTTPException: If the credentials are invalid.
    """
    user = await user_service.get_by_login(session, model.login)

    if model.oauth_access_token:
        oauth_service = get_oauthprovider_service(model.oauth_provider)
        if not oauth_service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Provider service not available.",
            )
        user_info = await oauth_service.get_user_info(request, model.oauth_access_token)

        email = user_info.get("login")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth token."
            )

        provider = await user_service.get_oauth_provider_by_name(
            session, model.oauth_provider
        )
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OAuth provider.",
            )

        oauth_user = await user_service.get_by_oauth(session, email)

        if oauth_user:
            if oauth_user.user is not None and oauth_user.user != user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This OAuth user is already linked to a different local user. Call support!",
                )

        if not user:
            user = await user_service.create_or_update(
                session,
                model.login,
                secrets.token_urlsafe(8),
                user_info.get("first_name"),
                user_info.get("last_name"),
            )
            await role_service.assign_role(session, user.id, settings.default_role_uuid)
            user = await user_service.get_by_login(session, model.login)

        if not oauth_user:
            await user_service.oauth_create_or_update(
                session,
                user,
                model.oauth_provider,
                email,
                user_info.get("first_name"),
                user_info.get("last_name"),
            )
        else:
            user = oauth_user.user
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot find association with a local User. Call support!",
                )

    elif not user or not user.check_password(model.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    roles, token_payload = await token_service.generate_payload(user)

    access_token = await token_service.create_access_token(token_payload)
    refresh_token = await token_service.create_refresh_token({"sub": user.login}, cache)

    await user_service.add_to_history(session, user.id)

    return SigninResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserWithRolesResponse(
            user_id=user.id,
            login=user.login,
            first_name=user.first_name,
            last_name=user.last_name,
            roles=roles,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Query(..., description="Refresh token of the user"),
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
    session: AsyncSession = Depends(get_session),
    cache: Redis = Depends(get_cache),
) -> TokenResponse:
    """
    Refresh the access token using a valid refresh token.

    **Endpoint**: POST `/refresh`

    :param refresh_token: The refresh token of the user.
    :param user_service: The user service to fetch history data.
    :param token_service: The token service to validate and issue tokens.
    :param cache: The Redis cache to check token validity.
    :param session: The database session.
    :return: A new access token along with the same refresh token.
    :raises HTTPException: If the refresh token is invalid or not found.
    """
    is_valid = await cache.get(refresh_token)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token not found"
        )

    payload = await token_service.verify_token(refresh_token)
    if not payload or payload.get("sup") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    login = payload.get("sub")
    user = await user_service.get_by_login(session, login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
        )

    _, token_payload = await token_service.generate_payload(user)

    new_access_token = await token_service.create_access_token(token_payload)

    return TokenResponse(access_token=new_access_token, refresh_token=refresh_token)


@router.post("/signout", status_code=204)
async def signout(
    refresh_token: str = Query(..., description="Refresh token of the user"),
    token_service: TokenService = Depends(get_token_service),
    cache: Redis = Depends(get_cache),
) -> None:
    """
    Sign out the user by invalidating the refresh token.

    **Endpoint**: POST `/signout`

    :param refresh_token: The refresh token to invalidate.
    :param token_service: The token service to handle invalidation.
    :param cache: The Redis cache to remove the refresh token.
    :return: HTTP status code 204 (No Content).
    """
    await token_service.invalidate_refresh_token(refresh_token, cache)
    return status.HTTP_204_NO_CONTENT


@router.get("/history/", response_model=list[HistoryResponse])
async def get_user_history(
    user_login: str = Query(..., description="The login of the user"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    session: AsyncSession = Depends(get_session),
) -> list[HistoryResponse]:
    """
    Retrieve login history for a user.

    **Endpoint**: GET `/history/`

    :param user_login: The login of the user whose history is requested.
    :param current_user: The currently logged-in user making the request.
    :param user_service: The user service to fetch history data.
    :param session: The database session.
    :return: A list of login history records.
    :raises HTTPException: If the user does not exist or access is unauthorized.
    """
    user = await user_service.get_by_login(session, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if current_user.login != user_login and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this user's login history.",
        )

    history = await user_service.get_login_history(session, user.id)
    return [
        HistoryResponse(user_id=item.id, login_time=item.created_at) for item in history
    ]


@router.get("/verify", response_model=UserWithRolesResponse)
async def verify_token(
    access_token: str = Query(..., description="Access token of the user"),
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
    session: AsyncSession = Depends(get_session),
) -> UserWithRolesResponse:
    """
    Verify the access token using.

    **Endpoint**: GET `/verify`

    :param access_token: The access token of the user.
    :param user_service: The user service to fetch history data.
    :param token_service: The token service to validate tokens.
    :return: If access token valid - return User info with roles.
    :raises HTTPException: If the access token is invalid or the user is not found.
    """
    payload = await token_service.verify_token(access_token)
    if not payload or payload.get("sup") != "access":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access token"
        )

    login = payload.get("sub")
    user = await user_service.get_by_login(session, login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    roles, _ = await token_service.generate_payload(user)

    user_response = UserWithRolesResponse(
        user_id=user.id,
        login=user.login,
        first_name=user.first_name,
        last_name=user.last_name,
        roles=roles,
    )

    return user_response
