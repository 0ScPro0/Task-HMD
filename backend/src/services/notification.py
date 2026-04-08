from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from database import Notification
from repositories import NotificationRepository
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
)
from services.base import BaseService
from utils.logger import log


class NotificationService(
    BaseService[
        Notification, NotificationCreate, NotificationUpdate, NotificationRepository
    ]
):
    """Service for working with Notification"""

    def __init__(
        self, session: AsyncSession, notification_repository: NotificationRepository
    ):
        super().__init__(
            repository=notification_repository,
            session=session,
        )

    @log
    async def get_all_notifications(self) -> List[NotificationResponse]:
        notifications = await self.repository.get_many(
            self.session, skip=0, limit=100, order_by=None
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
    async def update_notification(
        self, notification_id: int, notification: NotificationUpdate
    ) -> NotificationResponse:
        notification = await self.repository.update(
            self.session, notification_id, notification
        )
        return NotificationResponse.model_validate(notification)

    @log
    async def delete_notification(self, notification_id: int) -> NotificationResponse:
        notification = await self.repository.delete(self.session, notification_id)
        return NotificationResponse.model_validate(notification)
