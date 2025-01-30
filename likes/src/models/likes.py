from typing import Optional

from pydantic import BaseModel, Field


class Base(BaseModel):
    user_id: str = Field(..., description="ID of the user performing the action")
    film_id: str = Field(..., description="ID of the film")


class Rating(Base):
    score: Optional[float] = Field(None, description="Rating score, required for 'add'")


class Review(Base):
    review_id: Optional[str] = Field(
        None, description="ID of the review, required for 'update' or 'remove'"
    )
    content: Optional[str] = Field(
        None, description="Review text, required for 'add' or 'update'"
    )
