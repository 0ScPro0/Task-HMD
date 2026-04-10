from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.request import User
    from database.models.notification import Notification


class UserNotification(Base):
    __tablename__ = "user_notifications"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=None, nullable=True
    )

    # Chained entity
    notification_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("notifications.id"), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_notifications")
    notification: Mapped["Notification"] = relationship(
        "Notification", back_populates="user_notifications"
    )

    def __repr__(self) -> str:
        return f"<UserNotifications(id={self.id}, notification_id={self.notification_id}, user_id={self.user_id}, is_read={self.is_read})>"
