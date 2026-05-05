from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from schemas.user import UserBase, UserCreate, UserResponse


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_in: int
    refresh_token_expires_in: int


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    access_token_expires_in: int


class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=9, max_length=15)
    password: str = Field(..., min_length=8, max_length=72)


class RegisterRequest(BaseModel):
    email: Optional[EmailStr] = Field(None, max_length=255)
    name: str = Field(..., min_length=3, max_length=100)
    surname: str = Field(..., min_length=3, max_length=100)
    patronymic: Optional[str] = Field(None, min_length=3, max_length=100)
    address: Optional[str] = Field(None, min_length=3, max_length=100)
    apartment: Optional[str] = Field(None, min_length=1, max_length=20)
    phone: str = Field(..., min_length=9, max_length=15)
    password: str = Field(..., min_length=8, max_length=72)


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int


class RegisterResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int
    token_type: str = "bearer"
