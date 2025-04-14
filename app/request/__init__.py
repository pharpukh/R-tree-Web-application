__all__ = (
    "UserRequest",
    "create_request",
    "get_request_history",
    "get_requests_by_user",
    "create_user_request",
    "RequestCreate",
    "RequestOut",
    "router",
)

from fastapi import APIRouter

from .models import UserRequest
from .crud import create_request, get_requests_by_user
from .schemas import RequestCreate, RequestOut
from .views import create_user_request, get_request_history
from .views import router as request_router
router = APIRouter()
router.include_router(router=request_router,prefix="/requests")