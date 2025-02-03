from uuid import UUID

from pydantic import BaseModel


class RatedFilm(BaseModel):
    film_id: UUID
    score: float


class FilmResponse(BaseModel):
    film_id: UUID
    likes_count: int
    dislikes_count: int
    average_rating: float
    reviews_count: int
    favorites_count: int


class UserResponse(BaseModel):
    user_id: UUID
    liked_films: list[UUID]
    disliked_films: list[UUID]
    rated_films: list[RatedFilm]
    favorite_films: list[UUID]
