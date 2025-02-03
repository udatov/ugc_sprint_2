from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, Field


class RatedFilm(BaseModel):
    film_id: UUID
    score: float


class Review(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id: UUID
    film_id: UUID
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    likes_count: int = 0
    dislikes_count: int = 0

    class Settings:
        collection = "reviews"


class User(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    liked_films: list[UUID] = Field(default_factory=list)
    disliked_films: list[UUID] = Field(default_factory=list)
    rated_films: list[RatedFilm] = Field(default_factory=list)
    favorite_films: list[UUID] = Field(default_factory=list)

    class Settings:
        collection = "users"


class Film(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    likes_count: int = 0
    dislikes_count: int = 0
    average_rating: float = 0.0
    raiting_count: int = 0
    reviews_count: int = 0
    favorites_count: int = 0

    class Settings:
        collection = "films"
