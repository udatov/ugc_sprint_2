from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime


class RatedFilm(BaseModel):
    film_id: str
    score: float


class Review(Document):
    review_id: str = Field(alias="_id")
    user_id: str
    film_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    likes_count: int = 0
    dislikes_count: int = 0

    class Settings:
        collection = "reviews"


class User(Document):
    user_id: str = Field(alias="_id")
    liked_films: list[str] = Field(default_factory=list)
    disliked_films: list[str] = Field(default_factory=list)
    rated_films: list[RatedFilm] = Field(default_factory=list)
    favorite_films: list[str] = Field(default_factory=list)

    class Settings:
        collection = "users"


class Film(Document):
    film_id: str = Field(alias="_id")
    likes_count: int = 0
    dislikes_count: int = 0
    average_rating: float = 0.0
    raiting_count: int = 0
    reviews_count: int = 0
    favorites_count: int = 0

    class Settings:
        collection = "films"
