from fastapi import Request
from fastapi.datastructures import State
from sqladmin import ModelView
from database import User
from core.security import hash_password


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

    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request: Request[State]
    ) -> None:
        if is_created and "password_hash" in data and data["password_hash"]:
            data["password_hash"] = hash_password(data["password_hash"])
        return await super().on_model_change(data, model, is_created, request)
