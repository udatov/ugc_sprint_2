from likes.src.models import likes

VALID_CATEGORIES = {
    "favorite": {"topic": "favorite_events", "model": likes.FavoriteAction},
    "rating": {"topic": "rating_events", "model": likes.RatingAction},
    "review": {"topic": "review_events", "model": likes.ReviewAction},
    "watching": {"topic": "watching_events", "model": likes.WatchingAction},
    "searching": {"topic": "searching_events", "model": likes.SearchQuery},
}

VALID_ACTIONS = {
    "favorite": {"add", "remove"},
    "rating": {"add", "update"},
    "review": {"add", "update", "remove"},
    "watching": {"start", "stop"},
    "searching": {"query"},
}

# Kafka topics:

favorite_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
}

rating_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "score": "float",
}

review_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "review_id": "str",
    "content": "str",
}

watching_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "fully_watched": "bool",
    "stopped_at_time": "str",
}

searching_events = {
    "user_id": "str",
    "action": "str",
    "timestamp": "datetime",
    "query": "str",
    "search_by": "str",
}

# optional topic:
user_activity = {
    "user_id": "str",
    "category": "str",
    "action": "str",
    "details": {"user_id": "str", "film_id": "str", "action": "str"},
    "timestamp": "datetime",
}
