from sqladmin import ModelView
from database import UserNotification


class UserNotificationAdmin(ModelView, model=UserNotification):
    column_list = [
        UserNotification.id,
        UserNotification.user_id,
        UserNotification.notification_id,
        UserNotification.is_read,
        UserNotification.read_at,
    ]

    form_excluded_columns = [
        "created_at",
        "updated_at",
    ]
    can_create = False
