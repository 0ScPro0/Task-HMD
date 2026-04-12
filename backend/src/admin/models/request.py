from fastapi.datastructures import State
from fastapi import Request as FRequest
from sqladmin import ModelView

from api.dependencies import get_db_session, get_notification_service
from database import Request
from schemas.notification import NotificationCreate


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

    async def after_model_change(
        self, data: dict, model: Request, is_created: bool, request: FRequest[State]
    ) -> None:
        await super().after_model_change(data, model, is_created, request)

        if not is_created:
            async for session in get_db_session():
                notification_service = await get_notification_service(session)

                notification = NotificationCreate(
                    title="Изменение в заявке: " + data.get("title", "Заявка"),
                    body=data.get("description", ""),
                    request_id=model.id,
                    news_id=None,
                )

                created_notification = await notification_service.create_notification(
                    notification
                )
                await notification_service.send_notifications(
                    notification=created_notification
                )
                await session.commit()
                break
