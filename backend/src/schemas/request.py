from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from database import RequestStatus, RequestType


class RequestBase(BaseModel):
    type: RequestType
    title: str
    description: str
    status: RequestStatus
    admin_comment: Optional[str]


class RequestCreate(RequestBase):
    owner_id: int


class RequestUpdate(RequestBase):
    owner_id: int


class RequestResponse(RequestBase):
    id: int
    owner_id: int
    executor_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
