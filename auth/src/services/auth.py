import jwt
from core.config import settings
from db.basedb import get_session
from db.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.user import UserService, get_user_service
from sqlalchemy.ext.asyncio import AsyncSession

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """
    Retrieve the current authenticated user based on the JWT token.

    :param credentials: HTTP authorization credentials for the user.
    :param session: Database session for executing queries.
    :param user_service: Service for user-related database operations.
    :return: The current authenticated User object.
    :raises HTTPException: If the token is invalid or the user does not exist.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        login = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_user = await user_service.get_by_login(session, login)

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def get_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user has superuser privileges.

    :param current_user: The current authenticated user.
    :return: The current user object if they are a superuser.
    :raises HTTPException: If the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have superuser privileges",
        )
    return current_user
