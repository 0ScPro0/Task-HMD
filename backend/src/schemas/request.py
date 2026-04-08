from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

from database import RequestStatus, RequestType


class RequestBase(BaseModel):
    type: RequestType
    description: str
    status: RequestStatus
    admin_comment: Optional[str]


class RequestCreate(RequestBase):
    pass


class RequestUpdate(RequestBase):
    pass


class RequestResponse(RequestBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
