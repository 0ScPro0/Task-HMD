from sqladmin import ModelView
from database import Notification


class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id,
        Notification.user_id,
        Notification.title,
        Notification.is_read,
        Notification.request_id,
        Notification.news_id,
    ]

    form_excluded_columns = [
        "created_at",
        "updated_at",
    ]
