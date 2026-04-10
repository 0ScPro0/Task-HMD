from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class UserNotificationBase(BaseModel):
    is_read: bool
    user_id: int
    notification_id: int


class UserNotificationCreate(UserNotificationBase):
    is_read = False


class UserNotificationUpdate(UserNotificationBase):
    pass


class UserNotificationResponse(UserNotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    read_at: datetime

    model_config = ConfigDict(from_attributes=True)
