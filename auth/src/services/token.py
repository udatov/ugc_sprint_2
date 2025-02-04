from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Optional

import jwt
from core.config import settings
from db.models.user import User
from redis.asyncio import Redis


class TokenService:
    """
    Service class for handling token-related operations.
    """

    async def create_access_token(self, data: dict) -> jwt:
        """
        Generate an access token.

        :param data: The data to include in the token payload.
        :return: A JWT access token string.
        """
        to_encode = data.copy()
        to_encode.update(
            {
                "sup": "access",
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=settings.access_token_expire_in_minutes),
            }
        )
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    async def create_refresh_token(self, data: dict, cache: Redis) -> jwt:
        """
        Generate a refresh token and store it in the cache.

        :param data: The data to include in the token payload.
        :param cache: Redis cache for managing token validity.
        :return: A JWT refresh token string.
        """
        to_encode = data.copy()
        to_encode.update(
            {
                "sup": "refresh",
                "exp": datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_in_days),
            }
        )
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        expire_time = settings.refresh_token_expire_in_days * 24 * 60 * 60
        ping = await cache.ping()
        print(ping)
        await cache.set(encoded_jwt, "valid", ex=expire_time)

        return encoded_jwt

    async def verify_token(self, token: str) -> Optional[dict[str, any]]:
        """
        Verify the validity of a token.

        :param token: The token string to validate.
        :return: Decoded payload if the token is valid, otherwise None.
        """
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            return payload
        except jwt.exceptions.InvalidTokenError:
            return None

    async def invalidate_refresh_token(self, refresh_token: str, cache: Redis) -> None:
        """
        Invalidate a refresh token in the cache.

        :param refresh_token: The refresh token string to invalidate.
        :param cache: Redis cache to interact with.
        """
        await cache.delete(refresh_token)

    async def generate_payload(
        self, user: User
    ) -> tuple[list[dict[str, str]], dict[str, str]]:
        """
        Select roles for a user to dict.
        Generate a payload for acces token that includes full user info.

        :param user: User that playload is needed to generate.
        :return: User roles (dict) and Payload for acces token.
        """
        roles = [
            {"name": user_role.role.name}
            for user_role in user.role
            if user_role.role is not None
        ]

        token_payload = {
            "sub": user.login,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": roles,
        }
        return roles, token_payload


@lru_cache()
def get_token_service() -> TokenService:
    """
    Get an instance of TokenService.
    """
    return TokenService()
