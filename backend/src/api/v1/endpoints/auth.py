from fastapi import APIRouter, Depends

from api.dependencies import AuthService, get_auth_service
from core.security import get_current_user
from core.exceptions import PermissionDeniedError

from database import User

from schemas.auth import (
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    RegisterResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    """
    return await auth_service.register(request)


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate a user
    """
    return await auth_service.login(request)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Logout user
    """
    await auth_service.logout(current_user.id)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_request: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Refresh access token using refresh token
    """

    return await auth_service.refresh_token(refresh_request)
