from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import database, User, Request, Notification, News
from repositories import (
    user_repository,
    request_repository,
    notification_repository,
    user_notification_repository,
    news_repository,
)
from schemas.user import UserResponse
from services import (
    AuthService,
    UserService,
    RequestService,
    NotificationService,
    NewsService,
)


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


async def get_request_service(
    session: AsyncSession = Depends(get_db_session),
) -> RequestService:
    """Get request service"""
    return RequestService(session, request_repository)


async def get_notification_service(
    session: AsyncSession = Depends(get_db_session),
) -> NotificationService:
    """Get notification service"""
    return NotificationService(
        session,
        notification_repository,
        user_notification_repository,
        user_repository,
        request_repository,
    )


async def get_news_service(
    session: AsyncSession = Depends(get_db_session),
) -> NewsService:
    """Get news service"""
    return NewsService(session, news_repository)


__all__ = [
    "AuthService",
    "UserService",
    "RequestService",
    "NotificationService",
    "NewsService",
    "UserResponse",
    "get_db_session",
    "get_auth_service",
    "get_user_service",
    "get_request_service",
    "get_notification_service",
    "get_news_service",
]
