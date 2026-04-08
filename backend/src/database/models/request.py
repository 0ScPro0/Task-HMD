from typing import TYPE_CHECKING
import enum

from sqlalchemy import Integer, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.types.request import RequestStatus, RequestType

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.notification import Notification


class Request(Base):
    __tablename__ = "requests"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    type: Mapped[RequestType] = mapped_column(Enum(RequestType), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.NEW
    )
    admin_comment: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="requests")
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="request", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, user_id={self.user_id}, type={self.type}, status={self.status})>"
