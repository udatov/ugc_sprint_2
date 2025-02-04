import logging
from functools import lru_cache

import httpx
from core.config import settings
from fastapi import status

logger = logging.getLogger(settings.project)


class UgcService:
    """
    Service for handling User Generated Content (UGC) statistics.
    """

    async def send_stat(self, category: str, action: str, payload: dict) -> None:
        """
        Send statistics to the defined UGC API.

        :param category: The category of the UGC, indicating the type of content.
        :param action: The action to perform (e.g. 'add', 'update').
        :param payload: The data to send in the request body.
        :returns: None
        """
        url = f"{settings.UGC_API_URL}/{category}/{action}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)

                if response.status_code != status.HTTP_200_OK:
                    logger.error(
                        "Invalid request for category '%s' and action '%s': %s",
                        category,
                        action,
                        response.text,
                    )
                    return

                logger.info(
                    "Successfully sent stats for category '%s' and action '%s'.",
                    category,
                    action,
                )

            except httpx.RequestError as e:
                logger.error(
                    "Request error for category '%s' and action '%s': %s",
                    category,
                    action,
                    str(e),
                )
                return
            except Exception as e:
                logger.error(
                    "Internal error for category '%s' and action '%s': %s",
                    category,
                    action,
                    str(e),
                )
                return


@lru_cache()
def get_ugc_service() -> UgcService:
    """
    :returns: An instance of UgcService.
    """
    return UgcService()
