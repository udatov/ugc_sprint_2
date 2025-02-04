from api.v1 import oauth, role, user
from fastapi import APIRouter

router = APIRouter()


router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(role.router, prefix="/role", tags=["role"])
router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
