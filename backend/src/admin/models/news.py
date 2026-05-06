from fastapi import Request
from fastapi.datastructures import State
from sqladmin import ModelView

from api.dependencies import get_db_session, get_notification_service
from database import News
from schemas.notification import NotificationCreate


class NewsAdmin(ModelView, model=News):
    column_list = [
        News.id,
        News.title,
        News.is_published,
    ]

    form_excluded_columns = [
        "notifications",
        "created_at",
        "updated_at",
    ]

    async def after_model_change(
        self, data: dict, model: News, is_created: bool, request: Request[State]
    ) -> None:
        await super().after_model_change(data, model, is_created, request)

        if is_created:
            async for session in get_db_session():
                notification_service = await get_notification_service(session)

                notification = NotificationCreate(
                    title=data.get("title", "Новая новость"),
                    body=data.get("content", ""),
                    request_id=None,
                    news_id=model.id,
                )

                created_notification = await notification_service.create_notification(
                    notification
                )
                await notification_service.send_notifications(
                    notification=created_notification
                )
                await session.commit()
                break
