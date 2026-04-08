from repositories.base import BaseRepository

from repositories.user import UserRepository, user_repository
from repositories.request import RequestRepository, request_repository
from repositories.notification import NotificationRepository, notification_repository
from repositories.news import NewsRepository, news_repository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "RequestRepository",
    "NotificationRepository",
    "NewsRepository",
    "user_repository",
    "request_repository",
    "notification_repository",
    "news_repository",
]
