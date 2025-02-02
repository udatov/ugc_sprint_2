from pydantic import BaseModel


class FilmResponse(BaseModel):
    film_id: str
    likes_count: int
    dislikes_count: int
    average_rating: float
    reviews_count: int
    favorites_count: int


class UserResponse(BaseModel):
    user_id: str
    liked_films: list[str]
    disliked_films: list[str]
    rated_films: list[dict]
    favorite_films: list[str]
