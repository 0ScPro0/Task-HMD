from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_notification_service, NotificationService
from core.security import get_current_user
from database import User, Notification, UserNotification
from schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    FullNotificationResponse,
)
from utils.logger import log

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/user", response_model=FullNotificationResponse)
@log
async def get_user_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.get_user_notifications(
        user=current_user, skip=skip, limit=limit, order_by=UserNotification.created_at
    )


@router.post("/create", response_model=FullNotificationResponse)
@log
async def create_notification(
    notification: NotificationCreate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    created_notification = await notification_service.create_notification(
        notification=notification
    )


@router.post(
    "/user/{user_notification_id}/read", response_model=FullNotificationResponse
)
@log
async def read_notification(
    user_notification_id: int,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.read_notification(user_notification_id)
