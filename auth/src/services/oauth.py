from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any

from core.config import settings
from fastapi import HTTPException, Request, status
from httpx import AsyncClient
from slowapi import Limiter
from slowapi.util import get_remote_address
from utils.backoff import backoff

limiter = Limiter(key_func=get_remote_address)


class OauthAbstractService(ABC):
    def __init__(self):
        """
        Initialize the OAuth service.
        """
        self.auth_url = None

    @abstractmethod
    async def get_access_token(self, request: Request, code: str) -> str:
        """
        Retrieve the access token using an authorization code.

        :param request: The FastAPI Request object used for rate-limiting.
        :param code: The authorization code received from the provider after user authorization.
        :return: The access token for OAuth authentication.
        :raises HTTPException: If an error occurs while retrieving the access token.
        """

    @abstractmethod
    async def get_user_info(
        self, request: Request, access_token: str
    ) -> dict[str, Any]:
        """
        Retrieve user information using the access token.

        :param request: The FastAPI Request object used for rate-limiting.
        :param access_token: The access token for authentication with the provider.
        :return: A dictionary containing user information retrieved from the API.
        :raises HTTPException: If an error occurs while fetching user information.
        """


class OauthYandexService(OauthAbstractService):
    """
    Service for handling Yandex OAuth 2.0 authentication.
    """

    def __init__(self):
        """
        Initialize the OauthYandexService with necessary URLs and parameters.
        """
        self.auth_url = settings.yandex_oauth.auth_url

    @limiter.limit("20/minutes")
    @backoff()
    async def get_access_token(self, request: Request, code: str) -> str:
        """
        Retrieve the Yandex access token using an authorization code.

        :param request: The FastAPI Request object used for rate-limiting.
        :param code: The authorization code received from Yandex after user
                     authorization.
        :return: The access token for Yandex OAuth authentication.
        :raises HTTPException: If the request to Yandex returns an error or
                              if the response data contains an error.
        """
        token_url = settings.yandex_oauth.token_url
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.yandex_oauth.CLIENT_ID,
            "client_secret": settings.yandex_oauth.CLIENT_SECRET,
            "redirect_uri": settings.yandex_oauth.REDIRECT_URI,
        }

        async with AsyncClient() as client:
            response = await client.post(token_url, data=payload)
            response_data = response.json()

        if "error" in response_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=response_data.get("error_description"),
            )

        return response_data["access_token"]

    @limiter.limit("20/minutes")
    @backoff()
    async def get_user_info(
        self, request: Request, access_token: str
    ) -> dict[str, Any]:
        """
        Retrieve user information from Yandex using the access token.

        :param request: The FastAPI Request object used for rate-limiting.
        :param access_token: The access token for authentication with Yandex.
        :return: The user information retrieved from the Yandex API.
        :raises HTTPException: If an error occurs while trying to fetch user information.
        """
        async with AsyncClient() as client:
            user_info_response = await client.get(
                settings.yandex_oauth.login_url,
                headers={"Authorization": f"OAuth {access_token}"},
            )

        if user_info_response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Unable to fetch user info from Yandex."
            )

        return user_info_response.json()


oauth_services = {"yandex": OauthYandexService()}


@lru_cache()
def get_oauthprovider_service(provider: str) -> Any:
    """
    Retrieve the appropriate OAuth service class based on the provider name.

    :param provider: The name of the OAuth provider (e.g. 'yandex').
    :return: An instance of the corresponding OAuth service or None if not found.
    """
    return oauth_services.get(provider.lower(), None)
