from datetime import datetime
from functools import lru_cache
from uuid import UUID

from fastapi import HTTPException, status

from db.models import Film, RatedFilm, Review, User



class LikeService:
    async def get_or_create_user(self, user_id: str) -> User:
        """
        Get an existing user or create a new one if it does not exist.

        :param user_id: The ID of the user to retrieve or create.
        :returns: The User object corresponding to the provided user_id.
        """
        user_id = UUID(user_id)
        user = await User.find_one(User.id == user_id)
        if not user:
            user = User(id=user_id)
            await user.insert()
        return user

    async def get_or_create_film(self, film_id: str) -> Film:
        """
        Get an existing film or create a new one if it does not exist.

        :param film_id: The ID of the film to retrieve or create.
        :returns: The Film object corresponding to the provided film_id.
        """
        film = await Film.find_one(Film.id == film_id)
        if not film:
            film = Film(id=film_id)
            await film.insert()
        return film

    async def increment_value(
        self,
        user_id: str,
        film_id: str,
        user_field: str,
        film_field: str,
        increment_value: int,
        error_message: str,
    ) -> bool:
        """
        General method for handling boolean operations like adding/removing likes, dislikes, or favorites.

        :param user_id: The ID of the user performing the action.
        :param film_id: The ID of the film to which the action is related.
        :param user_field: The field in the user object to be modified (e.g., liked_films).
        :param film_field: The field in the film object to be modified (e.g., likes_count).
        :param increment_value: The value to increment or decrement (positive for addition, negative for removal).
        :param error_message: The error message to return if the operation fails.
        :returns: A boolean indicating the success of the operation.
        :raises HTTPException: If the user field or film field is invalid, or if the action cannot be performed.
        """
        user = await self.get_or_create_user(user_id)
        film = await self.get_or_create_film(film_id)

        user_field_value = getattr(user, user_field, None)
        if user_field_value is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid user field: {user_field} for {user}, and {user_field_value}",
            )

        if increment_value > 0:
            if film_id in getattr(user, user_field):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
            getattr(user, user_field).append(film_id)
        else:
            if film_id not in getattr(user, user_field):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
            getattr(user, user_field).remove(film_id)

        await user.save()

        setattr(film, film_field, max(0, getattr(film, film_field) + increment_value))
        await film.save()

        return True

    async def rate_film(self, user_id: str, film_id: str, rating: float) -> None:
        """
        Add or update a rating for a film by a user.

        :param user_id: The ID of the user rating the film.
        :param film_id: The ID of the film being rated.
        :param rating: The rating to assign to the film (should be between 0 and 10).
        :raises HTTPException: If the rating is out of bounds.
        """
        if rating < 0 or rating > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 0 and 10."
            )

        user = await self.get_or_create_user(user_id)
        film = await self.get_or_create_film(film_id)

        existing_rating = next(
            (r for r in user.rated_films if r.film_id == film_id), None
        )

        if existing_rating:
            total_score = (
                film.average_rating * film.raiting_count
                - existing_rating.score
                + rating
            )
            existing_rating.score = rating
        else:
            user.rated_films.append(RatedFilm(film_id=film_id, score=rating))
            total_score = film.average_rating * film.raiting_count + rating
            film.raiting_count += 1

        film.average_rating = (
            total_score / film.raiting_count if film.raiting_count > 0 else 0
        )

        await user.save()
        await film.save()

    async def unrate_film(self, user_id: str, film_id: str) -> None:
        """
        Remove a user's rating for a film.

        :param user_id: The ID of the user removing the rating.
        :param film_id: The ID of the film for which the rating is being removed.
        :raises HTTPException: If the user has not rated the film.
        """
        user = await self.get_or_create_user(user_id)
        film = await self.get_or_create_film(film_id)

        existing_rating = next(
            (r for r in user.rated_films if r.film_id == film_id), None
        )
        if not existing_rating:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rated film not found.")

        film.average_rating = (
            (film.average_rating * film.raiting_count - existing_rating.score)
            / (film.raiting_count - 1)
            if film.raiting_count > 1
            else 0
        )
        film.raiting_count -= 1
        user.rated_films.remove(existing_rating)

        await user.save()
        await film.save()

    async def add_or_update_review(
        self, user_id: str, film_id: str, content: str
    ) -> str:
        """
        Add a new review or update an existing review for a film by a user.

        :param user_id: The ID of the user adding or updating a review.
        :param film_id: The ID of the film being reviewed.
        :param content: The content of the review.
        :returns: The ID of the review.
        :raises HTTPException: If a review update fails.
        """
        user = await self.get_or_create_user(user_id)
        film = await self.get_or_create_film(film_id)

        review = await Review.find_one(
            Review.user_id == user.id, Review.film_id == film.id
        )

        if review:
            review.content = content
            review.timestamp = datetime.now()
            await review.save()
            return str(review.id)
        else:
            new_review = Review(
                user_id=user_id,
                film_id=film_id,
                content=content,
                timestamp=datetime.now(),
            )
            await new_review.insert()

        film.reviews_count += 1
        await film.save()

        return str(new_review.id)

    async def delete_review(self, user_id: str, film_id: str) -> None:
        """
        Delete a user's review for a film.

        :param user_id: The ID of the user deleting the review.
        :param film_id: The ID of the film for which the review is being deleted.
        :raises HTTPException: If the review is not found.
        """
        user = await self.get_or_create_user(user_id)
        film = await self.get_or_create_film(film_id)

        review = await Review.find_one(
            Review.user_id == user.id, Review.film_id == film.id
        )
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")

        review_id = review.id
        await review.delete()

        film = await self.get_or_create_film(film_id)
        film.reviews_count = max(0, film.reviews_count - 1)
        await film.save()

        return review_id

    async def get_film_info(self, film_id: str) -> dict:
        """
        Retrieve film statistics and details.

        :param film_id: The ID of the film to retrieve information for.
        :returns: A dictionary containing film statistics.
        :raises HTTPException: If the film cannot be found or created.
        """
        film = await self.get_or_create_film(film_id)
        return {
            "film_id": film.id,
            "likes_count": film.likes_count,
            "dislikes_count": film.dislikes_count,
            "average_rating": film.average_rating,
            "reviews_count": film.reviews_count,
            "favorites_count": film.favorites_count,
        }

    async def get_user_info(self, user_id: str) -> dict:
        """
        Retrieve user details including liked/disliked/rated/favorite films.

        :param user_id: The ID of the user to retrieve information for.
        :returns: A dictionary containing user information.
        """
        user = await self.get_or_create_user(user_id)
        return {
            "user_id": user.id,
            "liked_films": user.liked_films,
            "disliked_films": user.disliked_films,
            "rated_films": [
                {"film_id": rated.film_id, "score": rated.score}
                for rated in user.rated_films
            ],
            "favorite_films": user.favorite_films,
        }


@lru_cache()
def get_like_service() -> LikeService:
    """
    :returns: An instance of LikeService.
    """
    return LikeService()
