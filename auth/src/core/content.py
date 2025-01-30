import uuid
from datetime import datetime

from .config import settings

DEFAULT_ROLES = [
    {"id": uuid.uuid4(), "name": "anonymous", "created_at": datetime.now()},
    {
        "id": settings.default_role_uuid,
        "name": settings.default_role,
        "created_at": datetime.now(),
    },
    {"id": uuid.uuid4(), "name": "admin", "created_at": datetime.now()},
    {"id": uuid.uuid4(), "name": "subscriber", "created_at": datetime.now()},
]

DEFAULT_OAUTHPROVIDERS = [
    {"id": uuid.uuid4(), "name": "yandex", "created_at": datetime.now()}
]
