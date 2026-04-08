from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from repositories.base import BaseRepository
from database import Notification
from schemas.notification import NotificationCreate, NotificationUpdate

from utils.logger import log_database_queries


class NotificationRepository(
    BaseRepository[Notification, NotificationCreate, NotificationUpdate]
):
    """Class for Notification specific CRUD operations"""

    async def get_notification(
        self, session: AsyncSession, *, notification_id: int
    ) -> Optional[Notification]:
        """
        Get Notification by id

        Args:
            session: Database session
            notification_id: Specific Notification id

        Returns:
            Notification or None if not found
        """
        notification = await self.get(session, id=notification_id)
        return notification

    async def create_notification(
        self,
        session: AsyncSession,
        *,
        notification_object: Union[NotificationCreate, Dict[str, Any]]
    ) -> Notification:
        """
        Create Notification

        Args:
            session: Database session
            notification_object: NotificationCreate object or dict

        Returns:
            Created Notification object
        """
        notification = await self.create(session=session, object_in=notification_object)
        return notification
