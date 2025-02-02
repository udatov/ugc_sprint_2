from typing import Any, Type

from core.config import settings
from core.content import VALID_ACTIONS, VALID_CATEGORIES
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from services.stat import StatService, get_statistic_service

router = APIRouter()


@router.post("/{category}/{action}")
async def handle_action(
    category: str,
    action: str,
    payload: dict[str, Any],
    stat_service: StatService = Depends(get_statistic_service),
) -> dict[str, str]:
    """
    Endpoint for handling user actions dynamically.

    Valid actions; categories; payload:

        - like; add, remove; {user_id: str, film_id: Optional[str], review_id: Optional[str]}
        - dislike; add, remove; {user_id: str, film_id: Optional[str], review_id: Optional[str]}
        - favorite; add, remove; {user_id: str, film_id: str}
        - rating; add, update; {user_id: str, film_id: str, score: Optional[float]}
        - review; add, update, remove; {user_id: str, film_id: str, review_id: Optional[str], content: Optional[str]}
        - watching; start, stop, finish; {user_id: str, film_id: str, fully_watched: Optional[bool], stopped_at_time: Optional[str]}
        - searching; query; {user_id: Optional[str], query: str, search_by: Optional[str]}
    """
    category_config = VALID_CATEGORIES.get(category)
    if not category_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid category. Please use one of {list(VALID_CATEGORIES.keys())}",
        )

    if action not in VALID_ACTIONS.get(category, set()):
        valid_actions = VALID_ACTIONS.get(category, [])
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid action for category '{category}'. Please use one of {valid_actions}",
        )

    model: Type[BaseModel] = category_config["model"]
    try:
        parsed_payload = model(**payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid payload: {str(e)}",
        )

    topic = category_config["topic"]
    user_id = getattr(parsed_payload, "user_id", "anonymous") or "anonymous"
    event_data = parsed_payload.model_dump()
    event_data["action"] = action

    try:
        await stat_service.log_event(
            topic=topic,
            user_id=user_id,
            category=category,
            action=action,
            **{k: v for k, v in event_data.items() if k not in ("user_id", "action")},
        )
        if settings.USER_ACTIVITY_topic:
            await stat_service.log_user_activity(
                user_id=user_id, category=category, action=action, details=event_data
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error"
        )

    return {"message": f"Action '{action}' performed for category '{category}'"}
