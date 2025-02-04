from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthCheck(BaseModel):
    """
    Response model to validate and return when performing a health check.

    :param status: The status of the application (default is "OK").
    """

    status: str = "OK"


@router.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Check application status",
    response_description="Returns status code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
    include_in_schema=False,
)
def get_health() -> HealthCheck:
    """
    Check the application status.

    :return: HealthCheck object with the status of the application.
    """
    return HealthCheck(status="OK")
