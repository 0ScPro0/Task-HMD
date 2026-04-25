from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from repositories.base import BaseRepository
from database.models.user import User
from schemas.user import UserCreate, UserUpdate

from utils.logger import log_database_queries


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Class for User specific CRUD operations"""

    async def get_user(self, session: AsyncSession, *, user_id: int) -> Optional[User]:
        """
        Get user by id

        Args:
            session: Database session
            user_id: Specific user id

        Returns:
            User or None if not found
        """
        user = await self.get(session, id=user_id)
        return user

    async def get_user_by_phone_or_email(
        self,
        session: AsyncSession,
        *,
        phone: Optional[str] = None,
        email: Optional[EmailStr] = None,
    ) -> Optional[User]:
        """
        Get user by phone or email

        Args:
            session: Database session
            phone: str
            email: EmailStr

        Returns:
            User object or None if not found
        """
        fields = {"phone": phone, "email": email}
        user = await self.get_by_fields(session=session, fields=fields)
        return user

    async def create_user(
        self, session: AsyncSession, *, user_object: Union[UserCreate, Dict[str, Any]]
    ) -> User:
        """
        Create user

        Args:
            session: Database session
            user_object: UserCreate object or dict

        Returns:
            Created user object
        """
        user = await self.create(session=session, object_in=user_object)
        return user

    async def update_password(
        self, session: AsyncSession, *, user_id: int, password_hash: str
    ) -> Optional[User]:
        """
        Update user password

        Args:
            session: AsyncSession
            user_id: int
            password_hash: str

        Returns:
            Updated user object or None if not found
        """
        updated_user = await self.update_field(
            session=session,
            object_id=user_id,
            field_name="password_hash",
            field_value=password_hash,
        )
        return updated_user

    async def update_refresh_token(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        refresh_token: str,
        expires_at: datetime,
    ) -> Optional[User]:
        """
        Update user refresh token and its expiration time

        Args:
            session: Database session
            user_id: int
            refresh_token: str
            expires_at: datetime

        Returns:
            Updated user object or None if not found
        """
        updated_user = await self.update_fields(
            session=session,
            object_id=user_id,
            fields={
                "refresh_token": refresh_token,
                "refresh_token_expires_at": expires_at,
            },
        )
        return updated_user

    async def clear_refresh_token(self, session: AsyncSession, *, user_id: int) -> bool:
        """
        Clear user refresh token (set to None)

        Args:
            session: Database session
            user_id: int

        Returns:
            True if successful, False otherwise
        """
        updated_user = await self.update_fields(
            session=session,
            object_id=user_id,
            fields={"refresh_token": None, "refresh_token_expires_at": None},
        )

        if (
            updated_user.refresh_token is None
            and updated_user.refresh_token_expires_at is None
        ):
            return True

        return False

    async def activate(self, session: AsyncSession, *, user_id: int) -> Optional[User]:
        """
        Activate user

        Args:
            session: Database session
            user_id: int

        Returns:
            Activated user object or None if not found
        """
        updated_user = await self.update_field(
            session=session, object_id=user_id, field_name="is_active", field_value=True
        )
        return updated_user

    async def deactivate(
        self,
        session: AsyncSession,
        *,
        user_id: int,
    ) -> Optional[User]:
        """
        Deactivate user

        Args:
            session: Database session
            user_id: int

        Returns:
            Deactivated user object or None if not found
        """
        updated_user = await self.update_field(
            session=session,
            object_id=user_id,
            field_name="is_active",
            field_value=False,
        )
        return updated_user

    async def delete_user(
        self, session: AsyncSession, *, user_id: int
    ) -> Optional[User]:
        """
        Delete user

        Args:
            session: Database session
            user_id: int

        Returns:
            Deleted user object or None if not found
        """
        deleted_user = await self.delete(session=session, id=user_id)
        return deleted_user

    async def is_active(self, session: AsyncSession, *, user_id: int) -> bool:
        """
        Check if user is active

        Args:
            session: Database session
            user_id: int

        Returns:
            bool: True if user is active, False otherwise
        """
        user = await self.get(session=session, id=user_id)
        return user.is_active if user else False


user_repository = UserRepository(User)
