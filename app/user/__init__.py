__all__ = (
    "User",
    "UserOut",
    "UserCreate",
    "router",
    "get_current_user",
    "Token",
)

from .models import User
from .schemas import UserOut, UserCreate
from fastapi import APIRouter
from .views import router as users_router
from .dependencies import get_current_user
from .schemas import Token

router = APIRouter()
router.include_router(router=users_router, prefix="/users")
