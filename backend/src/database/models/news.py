from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.notification import Notification


class News(Base):
    __tablename__ = "news"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="news", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<News(id={self.id}, title={self.title[:50]}, is_published={self.is_published})>"
