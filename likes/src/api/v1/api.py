from api.v1 import film, user
from fastapi import APIRouter

router = APIRouter()

router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(film.router, prefix="/film", tags=["film"])
