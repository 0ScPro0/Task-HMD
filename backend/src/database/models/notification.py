from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.request import Request
    from database.models.news import News
    from database.models.user_notification import UserNotification


class Notification(Base):
    __tablename__ = "notifications"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)

    # Chained entity (optional)
    request_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("requests.id"), nullable=True
    )
    news_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("news.id"), nullable=True
    )

    # Relationships
    user_notifications: Mapped[List["UserNotification"]] = relationship(
        "UserNotification", back_populates="notification", cascade="all, delete-orphan"
    )
    request: Mapped["Optional[Request]"] = relationship(
        "Request", back_populates="notifications"
    )
    news: Mapped["Optional[News]"] = relationship(
        "News", back_populates="notifications"
    )

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, request_id={self.request_id}, news_id={self.news_id})>"
