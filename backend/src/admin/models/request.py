from sqladmin import ModelView
from database import Request


class RequestAdmin(ModelView, model=Request):
    column_list = [
        Request.id,
        Request.owner_id,
        Request.executor_id,
        Request.type,
        Request.title,
        Request.status,
        Request.admin_comment,
    ]

    form_excluded_columns = [
        "notifications",
        "created_at",
        "updated_at",
    ]

    can_create = False
