from typing import TYPE_CHECKING, Optional
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

    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    executor_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    type: Mapped[RequestType] = mapped_column(Enum(RequestType), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.NEW
    )
    admin_comment: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", foreign_keys=[owner_id], back_populates="owned_requests"
    )
    executor: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[executor_id], back_populates="executed_requests"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="request", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, owner_id={self.owner_id}, type={self.type}, status={self.status})>"
