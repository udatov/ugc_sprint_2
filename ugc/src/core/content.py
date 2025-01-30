from models import actions

VALID_CATEGORIES = {
    "dislike": {"topic": "like_events", "model": actions.BaseAction},
    "like": {"topic": "like_events", "model": actions.BaseAction},
    "favorite": {"topic": "like_events", "model": actions.BaseAction},
    "rating": {"topic": "rating_events", "model": actions.RatingAction},
    "review": {"topic": "review_events", "model": actions.ReviewAction},
    "watching": {"topic": "watching_events", "model": actions.WatchingAction},
    "searching": {"topic": "searching_events", "model": actions.SearchQuery},
}

VALID_ACTIONS = {
    "dislike": {"add", "remove"},    
    "like": {"add", "remove"},
    "favorite": {"add", "remove"},
    "rating": {"add", "update"},
    "review": {"add", "update", "remove"},
    "watching": {"start", "stop"},
    "searching": {"query"},
}

# Kafka topics:
like_events = {
    "user_id": "str",
    "category": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
}

rating_events = {
    "user_id": "str",
    "category": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "score": "float",
}

review_events = {
    "user_id": "str",
    "category": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "review_id": "str",
    "content": "str",
}

watching_events = {
    "user_id": "str",
    "category": "str",
    "action": "str",
    "timestamp": "datetime",
    "film_id": "str",
    "fully_watched": "bool",
    "stopped_at_time": "str",
}

searching_events = {
    "user_id": "str",
    "category": "str",
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
