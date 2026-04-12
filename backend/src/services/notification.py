from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.exceptions import ValidationError, NotFoundError, NoRecipientsError
from database import (
    User,
    Notification,
    UserNotification,
    Request,
    RequestType,
    UserRole,
)
from repositories import (
    NotificationRepository,
    UserNotificationRepository,
    UserRepository,
    RequestRepository,
)
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
        user_repository: UserRepository,
        request_repository: RequestRepository,
    ):
        self.session = session
        self.notification_repository = notification_repository
        self.user_notification_repository = user_notification_repository
        self.user_repository = user_repository
        self.request_repository = request_repository

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

    @log
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
        if notification.request_id and notification.news_id:
            raise ValidationError(
                "Notification cannot have both request_id and news_id"
            )
        created_notification = await self.notification_repository.create_notification(
            self.session, notification_object=notification
        )
        return created_notification

    @log
    async def send_notifications(
        self,
        *,
        notification: Notification,
    ) -> FullNotificationResponse:
        """
        Create UserNotification to all users, which meet the conditions:
        1) if notification.news_id != None - all users
        2) if notification.request_id != None - to users with same role

        Args:
            notification: Notification object to be checked

        Returns:
            FullNotificationResponse that was sent to users
        """
        un = None  # user notification

        if notification.news_id is not None:
            # Create notification for all active users
            users = await self.user_repository.get_many(
                self.session, skip=0, limit=10000, order_by=None
            )
            for target_user in users:
                if target_user.is_active:
                    # Last user notification will be used to return
                    un = await self.user_notification_repository.create_user_notification(
                        self.session,
                        user_notification=UserNotificationCreate(
                            user_id=target_user.id,
                            notification_id=notification.id,
                            is_read=False,
                        ),
                    )

        elif notification.request_id is not None:
            # Create notification for users with specific roles based on request
            # Get request to determine target roles
            request = await self.request_repository.get_request(
                self.session, request_id=notification.request_id
            )
            if not request:
                raise NotFoundError("Request not found")

            if request:
                # Determine target roles based on request type
                # Always notify admin
                target_roles = [UserRole.ADMIN]

                # Map request type to relevant role
                type_to_role = {
                    RequestType.PLUMBER: UserRole.PLUMBER,
                    RequestType.ELECTRICIAN: UserRole.ELECTRICIAN,
                }
                role = type_to_role.get(request.type)
                if role:
                    target_roles.append(role)

                # Get users with target roles
                all_users = await self.user_repository.get_many(
                    self.session, skip=0, limit=10000, order_by=None
                )
                for target_user in all_users:
                    if target_user.is_active and target_user.role in target_roles:
                        # Last user notification will be used to return
                        un = await self.user_notification_repository.create_user_notification(
                            self.session,
                            user_notification=UserNotificationCreate(
                                user_id=target_user.id,
                                notification_id=notification.id,
                                is_read=False,
                            ),
                        )

        if not un:
            raise NoRecipientsError("No recipients found for notification")

        return FullNotificationResponse(
            is_read=un.is_read,
            user_id=un.user_id,
            notification_id=notification.id,
            id=un.id,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
            read_at=un.read_at,
            title=notification.title,
            body=notification.body,
        )

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
