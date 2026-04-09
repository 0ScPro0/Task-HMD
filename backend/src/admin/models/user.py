from sqladmin import ModelView
from database import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.role,
        User.is_active,
        User.name,
        User.surname,
        User.patronymic,
        User.email,
        User.phone,
        User.address,
        User.apartment,
    ]

    form_excluded_columns = [
        "requests",
        "notifications",
        "created_at",
        "updated_at",
        "refresh_token",
        "refresh_token_expires_at",
    ]
