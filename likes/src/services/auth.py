from functools import lru_cache
from typing import Optional

import backoff
import httpx
from core.config import settings
from fastapi import HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


class PermService:
    """
    Service for managing access to content. Provides methods to check user validity.
    """

    @limiter.limit("20/minutes")
    @backoff.on_exception(
        backoff.expo, (httpx.HTTPStatusError, httpx.RequestError), max_time=60
    )
    async def is_validuser(self, request: Request, access_token: str) -> Optional[str]:
        """
        Check if a user is a subscriber based on their access token.

        :param request: The FastAPI Request object used for rate-limiting.
        :param access_token: The access token of the user to be checked.
        :return: USER ID if the user is valid, False otherwise.
        :raises HTTPException: If the request to the API fails or if the
            response indicates an invalid credential or request.
        :raises httpx.RequestError: If there is a network-related error
            while making the request.
        """
        url = settings.AUTH_API_URL

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{url}?access_token={access_token}")
                if response.status_code != status.HTTP_200_OK:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid token or User not authenticated",
                    )

                data = response.json()
                if not data or not data["user_id"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid token or User not authenticated",
                    )

                return data["user_id"]

            except httpx.RequestError:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="We're sorry, but our service is currently experiencing high demand.Please try again later.",
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )


@lru_cache()
def get_perm_service() -> PermService:
    """
    :returns: An instance of PermService.
    """
    return PermService()
