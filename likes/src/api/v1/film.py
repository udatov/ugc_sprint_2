from typing import Any, Optional

from core.content import FILM_VALID_CATEGORIES
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from schemas.responses import FilmResponse
from services.auth import PermService, get_perm_service
from services.like import LikeService, get_like_service
from services.ugc import UgcService, get_ugc_service

router = APIRouter()


@router.post("/{film_id}/{category}")
async def add_film_status(
    film_id: str,
    category: str,
    request: Request,
    payload: Optional[dict[str, Any]] = None,
    like_service: LikeService = Depends(get_like_service),
    auth_service: PermService = Depends(get_perm_service),
    ugc_service: UgcService = Depends(get_ugc_service),
    access_token: str = Query(..., description="Access token of the user"),
) -> dict:
    """
    Add a like, dislike, or favorite for a film, or post a review or rate a film.
    """
    user_id = await auth_service.is_validuser(request, access_token)

    if category == 'review':
        if not payload or "content" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review content is required.")
        review_id = await like_service.add_or_update_review(user_id, film_id, payload["content"])
        ugc_payload = {
            "user_id": user_id,
            "film_id": film_id,
            "review_id": review_id,
            "content": payload["content"]
        }
        await ugc_service.send_stat(category, "add", ugc_payload)
        return {"message": "Review added successfully.", "review_id": review_id}

    if category == 'rating':
        if not payload or "rating" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating is required.")
        await like_service.rate_film(user_id, film_id, payload["rating"])
        ugc_payload = {
            "user_id": user_id,
            "film_id": film_id,
            "score": payload["rating"]
        }
        await ugc_service.send_stat(category, "add", ugc_payload)
        return {"message": f"Film rated successfully with score {payload['rating']}."}

    category_config = FILM_VALID_CATEGORIES.get(category)
    if not category_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category. Please use one of {list(FILM_VALID_CATEGORIES.keys())}",
        )

    await like_service.increment_value(user_id, film_id, category_config["user_field"],
                                       category_config["film_field"], 1, error_message=f"Cannot add {category} as it already exists.")
    ugc_payload = {
        "user_id": user_id,
        "film_id": film_id,
    }
    await ugc_service.send_stat(category, "add", ugc_payload)
    return {"message": f"{category} added successfully."}


@router.delete("/{film_id}/{category}")
async def delete_film_status(
    film_id: str,
    category: str,
    request: Request,
    like_service: LikeService = Depends(get_like_service),
    auth_service: PermService = Depends(get_perm_service),
    ugc_service: UgcService = Depends(get_ugc_service),
    access_token: str = Query(..., description="Access token of the user"),
) -> dict:
    """
    Remove like, dislike, or favorite for a film, or delete a review or remove a rating.
    """
    user_id = await auth_service.is_validuser(request, access_token)

    if category == 'review':
        review_id = await like_service.delete_review(user_id, film_id)
        ugc_payload = {
            "user_id": user_id,
            "film_id": film_id,
            "review_id": review_id,
        }
        await ugc_service.send_stat(category, "remove", ugc_payload)
        return {"message": "Review deleted successfully."}

    if category == 'rating':
        await like_service.unrate_film(user_id, film_id)
        ugc_payload = {
            "user_id": user_id,
            "film_id": film_id,
        }
        await ugc_service.send_stat(category, "remove", ugc_payload)
        return {"message": "Rating removed successfully."}

    category_config = FILM_VALID_CATEGORIES.get(category)
    if not category_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category. Please use one of {list(FILM_VALID_CATEGORIES.keys())}",
        )

    await like_service.increment_value(user_id, film_id, category_config["user_field"], category_config["film_field"],
                                       -1, error_message=f"Cannot remove {category} as it does not exist.")
    ugc_payload = {
        "user_id": user_id,
        "film_id": film_id,
    }
    await ugc_service.send_stat(category, "remove", ugc_payload)
    return {"message": f"{category} removed successfully."}


@router.put("/{film_id}/{category}")
async def update_film_status(
    film_id: str,
    category: str,
    request: Request,
    payload: dict[str, Any],
    like_service: LikeService = Depends(get_like_service),
    auth_service: PermService = Depends(get_perm_service),
    ugc_service: UgcService = Depends(get_ugc_service),
    access_token: str = Query(..., description="Access token of the user"),
) -> dict:
    """
    Update a review or rating for a film by a user.
    """
    user_id = await auth_service.is_validuser(request, access_token)

    if category == "review":
        if not payload or "content" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New review content is required.")
        review_id = await like_service.add_or_update_review(user_id, film_id, payload["content"])
        ugc_payload = {
            "user_id": user_id,
            "film_id": film_id,
            "review_id": review_id,
            "content": payload["content"]
        }
        await ugc_service.send_stat(category, "update", ugc_payload)
        return {"message": "Review updated successfully."}

    if category == "rating":
        if not payload or "rating" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New rating is required.")
        await like_service.rate_film(user_id, film_id, payload["rating"])
        ugc_payload = {
            "user_id": user_id,
            "film_id": film_id,
            "score": payload["rating"]
        }
        await ugc_service.send_stat(category, "update", ugc_payload)
        return {"message": f"Rating updated successfully to {payload['rating']}."}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid category '{category}'. Only 'review' and 'rating' can be updated.",
    )


@router.get("/{film_id}", response_model=FilmResponse)
async def get_film(
    film_id: str,
    request: Request,
    like_service: LikeService = Depends(get_like_service),
    auth_service: PermService = Depends(get_perm_service),
    access_token: str = Query(..., description="Access token of the user")
) -> dict:
    """
    Retrieve film details by film_id.
    """
    await auth_service.is_validuser(request, access_token)
    film_info = await like_service.get_film_info(film_id)
    return film_info
