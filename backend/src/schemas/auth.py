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


class LoginRequest(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class RegisterRequest(UserBase):
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
