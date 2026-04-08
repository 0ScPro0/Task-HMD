from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import database, User, Request, Notification, News
from repositories import user_repository
from schemas.user import UserResponse
from services import AuthService, UserService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async for session in database.get_session():
        try:
            yield session
        finally:
            await session.close()
        break


async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthService:
    """Get auth service"""
    return AuthService(session, user_repository)


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    """Get user service"""
    return UserService(session, user_repository)


__all__ = [
    "AuthService",
    "UserService",
    "UserResponse",
    "get_db_session",
    "get_auth_service",
    "get_user_service",
]
