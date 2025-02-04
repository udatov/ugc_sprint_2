from typing import Optional

from pydantic import BaseModel, Field


class Like(BaseModel):
    user_id: str = Field(..., description="ID of the user performing the action")
    film_id: Optional[str] = Field(None, description="ID of the film")
    review_id: Optional[str] = Field(None, description="ID of the review")


class BaseAction(BaseModel):
    user_id: str = Field(..., description="ID of the user performing the action")
    film_id: str = Field(..., description="ID of the film")


class RatingAction(BaseAction):
    score: Optional[float] = Field(None, description="Rating score, required for 'add'")


class ReviewAction(BaseAction):
    review_id: Optional[str] = Field(
        None, description="ID of the review, required for 'update' or 'remove'"
    )
    content: Optional[str] = Field(
        None, description="Review text, required for 'add' or 'update'"
    )


class WatchingAction(BaseAction):
    fully_watched: Optional[bool] = Field(
        False, description="Whether the film was fully watched"
    )
    stopped_at_time: Optional[str] = Field(
        None, description="Playback progress in seconds"
    )


class SearchQuery(BaseModel):
    user_id: Optional[str] = Field(
        None, description="User ID for logging purposes; optional for anonymous users"
    )
    query: str = Field(..., description="Search query")
    search_by: Optional[str] = Field(
        None, description="Search by 'film_name', 'person_name', or 'genre'"
    )
