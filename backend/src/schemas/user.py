from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

from database import UserRole


class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255)
    name: str = Field(..., min_length=3, max_length=100)
    surname: str = Field(..., min_length=3, max_length=100)
    patronymic: Optional[str] = Field(None, min_length=3, max_length=100)
    address: str = Field(..., min_length=3, max_length=100)
    apartment: str = Field(..., min_length=1, max_length=20)
    phone: str = Field(..., min_length=9, max_length=15)
    role: UserRole = Field(UserRole.RESIDENT)


class UserCreate(UserBase):
    password_hash: str = Field(
        ...,
        min_length=8,
        max_length=255,
    )

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    refresh_token: Optional[str] = Field(None, max_length=512)
    refresh_token_expires_at: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")


class UserUpdatePassword(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    id: int
    refresh_token: Optional[str] = None
    refresh_token_expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
