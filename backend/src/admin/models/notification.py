from sqladmin import ModelView
from database import Notification


class NotificationAdmin(ModelView, model=Notification):
    column_list = [
        Notification.id,
        Notification.title,
        Notification.request_id,
        Notification.news_id,
    ]

    form_excluded_columns = [
        "created_at",
        "updated_at",
    ]
    can_create = False
