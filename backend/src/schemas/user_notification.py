from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class UserNotificationBase(BaseModel):
    is_read: bool = Field(False)
    user_id: int
    notification_id: int


class UserNotificationCreate(UserNotificationBase):
    pass


class UserNotificationUpdate(UserNotificationBase):
    pass


class UserNotificationResponse(UserNotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    read_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
