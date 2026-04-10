from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database import User, Notification, UserNotification
from repositories import NotificationRepository, UserNotificationRepository
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    FullNotificationResponse,
)
from schemas.user_notification import UserNotificationCreate
from services.base import BaseService
from utils.logger import log


class NotificationService(BaseService):
    """Service for working with Notification"""

    def __init__(
        self,
        session: AsyncSession,
        notification_repository: NotificationRepository,
        user_notification_repository: UserNotificationRepository,
    ):
        self.session = (session,)
        self.notification_repository = notification_repository
        self.user_notification_repository = user_notification_repository

    @log
    async def get_all_notifications(
        self, skip: int = 0, limit: int = 100, order_by: Optional[Any] = None
    ) -> List[NotificationResponse]:
        notifications = await self.repository.get_many(
            self.session, skip=skip, limit=limit, order_by=order_by
        )
        return [
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ]

    @log
    async def get_notification(self, notification_id: int) -> NotificationResponse:
        notification = await self.repository.get(self.session, notification_id)
        return NotificationResponse.model_validate(notification)

    @log
    async def get_user_notifications(
        self,
        user: User,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        order_by: Optional[int] = None,
    ) -> List[FullNotificationResponse]:
        user_notifications = (
            await self.user_notification_repository.get_user_notifications(
                self.session, user_id=user.id, skip=skip, limit=limit, order_by=order_by
            )
        )
        responses = []
        for un in user_notifications:
            responses.append(
                FullNotificationResponse(
                    is_read=un.is_read,
                    user_id=un.user_id,
                    notification_id=un.notification_id,
                    id=un.id,
                    created_at=un.created_at,
                    updated_at=un.updated_at,
                    read_at=un.read_at,
                    title=un.notification.title,
                    body=un.notification.body,
                )
            )
        return responses

    async def read_notification(
        self, user_notification_id: int
    ) -> FullNotificationResponse:
        un = await self.user_notification_repository.read_user_notification(
            self.session, user_notification_id=user_notification_id
        )
        return FullNotificationResponse(
            is_read=un.is_read,
            user_id=un.user_id,
            notification_id=un.notification_id,
            id=un.id,
            created_at=un.created_at,
            updated_at=un.updated_at,
            read_at=un.read_at,
            title=un.notification.title,
            body=un.notification.body,
        )

    @log
    async def create_notification(
        self, notification: NotificationCreate
    ) -> Notification:
        created_notification = await self.notification_repository.create_notification(
            self.session, notification_object=notification
        )
        return created_notification

    async def create_user_notification(
        self,
        *,
        user: User,
        user_notification: UserNotificationCreate,
        notification: Notification,
    ):
        # TODO make create user notification logic
        # if notification.news_id != None - all users
        # if notification.request_id != None - to roles
        ...

    @log
    async def update_notification(
        self, notification_id: int, notification: NotificationUpdate
    ) -> NotificationResponse:
        updated_notification = await self.repository.update(
            self.session, update_object_id=notification_id, object_in=notification
        )
        return NotificationResponse.model_validate(updated_notification)

    @log
    async def delete_notification(self, notification_id: int) -> NotificationResponse:
        notification = await self.repository.delete(self.session, id=notification_id)
        return NotificationResponse.model_validate(notification)
