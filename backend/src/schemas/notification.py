from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from schemas.user_notification import UserNotificationResponse


class NotificationBase(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str


class NotificationCreate(NotificationBase):
    request_id: Optional[int]
    news_id: Optional[int]


class NotificationUpdate(NotificationBase):
    request_id: Optional[int]
    news_id: Optional[int]


class NotificationResponse(NotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FullNotificationResponse(NotificationResponse, UserNotificationResponse):
    pass
