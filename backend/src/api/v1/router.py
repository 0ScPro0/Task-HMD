from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.users import router as user_router
from api.v1.endpoints.requests import router as request_router
from api.v1.endpoints.notifications import router as notification_router
from api.v1.endpoints.news import router as news_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(request_router)
router.include_router(notification_router)
router.include_router(news_router)
