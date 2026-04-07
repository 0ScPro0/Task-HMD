from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database.types.user import UserRole
from database.models.base import Base

if TYPE_CHECKING:
    from database.models.request import Request
    from database.models.notification import Notification


class User(Base):
    __tablename__ = "users"

    email: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None
    )
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    apartment: Mapped[str] = mapped_column(String(20), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True, unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.RESIDENT)

    # Relationships
    requests: Mapped[list["Request"]] = relationship(
        "Request", back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
