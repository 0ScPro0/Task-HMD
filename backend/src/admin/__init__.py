from sqladmin import Admin
from sqladmin.models import ModelView
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI

from admin.auth import AdminAuthBackend
from database import database
from core.config import settings

from admin.models.user import UserAdmin
from admin.models.news import NewsAdmin
from admin.models.notification import NotificationAdmin
from admin.models.user_notification import UserNotificationAdmin
from admin.models.request import RequestAdmin


def setup_admin(app: FastAPI, dev_mode: bool = False):

    # Add session middleware (required for SQLAdmin)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.security.secret_key,
        session_cookie="admin_session",
        max_age=3600,  # 1 hour session
        same_site="lax",
    )

    # Create authentication backend
    authentication_backend = AdminAuthBackend(secret_key=settings.security.secret_key)
    if dev_mode:
        authentication_backend = None

    # Create admin interface
    admin = Admin(
        app,
        database.engine,
        title="Admin Panel",
        base_url="/admin",
        authentication_backend=authentication_backend,
    )

    # Register all views
    admin.add_view(UserAdmin)
    admin.add_view(NewsAdmin)
    admin.add_view(NotificationAdmin)
    admin.add_view(UserNotificationAdmin)
    admin.add_view(RequestAdmin)

    return admin


__all__ = ["setup_admin"]
