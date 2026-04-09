from sqladmin import ModelView
from database import News


class NewsAdmin(ModelView, model=News):
    column_list = [
        News.id,
        News.title,
        News.is_published,
        News.content,
    ]

    form_excluded_columns = [
        "notifications",
        "created_at",
        "updated_at",
    ]
