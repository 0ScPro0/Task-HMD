from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime


class NewsBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str
    is_published: bool = Field(False)


class NewsCreate(NewsBase):
    pass


class NewsUpdate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
