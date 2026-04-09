from sqladmin import ModelView
from database import Request


class RequestAdmin(ModelView, model=Request):
    column_list = [
        Request.id,
        Request.user_id,
        Request.type,
        Request.title,
        Request.status,
        Request.admin_comment,
    ]

    form_excluded_columns = [
        "notifications",
    ]
