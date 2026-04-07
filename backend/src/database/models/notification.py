from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.request import User
    from database.models.request import Request
    from database.models.news import News


class Notification(Base):
    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    # Chinned entity (optional)
    request_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("requests.id"), nullable=True
    )
    news_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("news.id"), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    request: Mapped["Request | None"] = relationship(
        "Request", back_populates="notifications"
    )
    news: Mapped["News | None"] = relationship("News", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, is_read={self.is_read})>"
