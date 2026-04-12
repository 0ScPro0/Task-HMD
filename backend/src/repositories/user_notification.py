from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from repositories.base import BaseRepository
from database import UserNotification
from schemas.user_notification import UserNotificationCreate, UserNotificationUpdate

from utils.logger import log_database_queries


class UserNotificationRepository(
    BaseRepository[UserNotification, UserNotificationCreate, UserNotificationUpdate]
):
    """Class for UserNotification specific CRUD operations"""

    async def get_user_notifications(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        skip: Optional[int] = 0,
        limit: Optional[int] = 0,
        order_by: Optional[Any] = None,
    ):
        """
        Get all UserNotification

        Args:
            session: Database session
            user_id: Specific User id

        Returns:
            List of UserNotification or None if not found
        """
        return await self.get_by_field_many(
            session=session,
            field_name="user_id",
            field_value=user_id,
            skip=skip,
            limit=limit,
            order_by=order_by,
            relationships=["notification"],
        )

    async def create_user_notification(
        self,
        session: AsyncSession,
        *,
        user_notification: Union[UserNotificationCreate, Dict[str, Any]],
    ):
        """
        Create UserNotification

        Args:
            session: Database session
            user_notification: UserNotification or dict

        Returns:
            List of UserNotification or None if not found
        """
        return await self.create(session=session, object_in=user_notification)

    async def read_user_notification(
        self,
        session: AsyncSession,
        *,
        user_notification_id: int,
    ):
        """
        Set UserNotification.is_read to True

        Args:
            session: Database session
            user_id: Specific User id

        Returns:
            True if succes, otherwise False
        """
        return await self.update_field(
            session=session,
            object_id=user_notification_id,
            field_name="is_read",
            field_value=True,
        )


user_notification_repository = UserNotificationRepository(UserNotification)
