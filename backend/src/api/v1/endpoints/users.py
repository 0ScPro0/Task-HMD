from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_user_service, UserService
from core.security import get_current_user, get_current_admin
from database import User
from schemas.user import UserResponse, UserUpdate
from utils.logger import log

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
@log
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile"""
    return current_user


@router.patch("/me", response_model=UserResponse)
@log
async def update_current_user_profile(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update current user profile"""
    return await user_service.update_user(user_id=current_user.id, user=request)


@router.get("", response_model=List[UserResponse])
@log
async def get_users(
    skip: int = Query(0, ge=0, le=100),
    limit: int = Query(100, ge=1, le=1000),
    admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
):
    """User list"""
    return await user_service.get_users(skip=skip, limit=limit, order_by=User.id)


@router.get("/{user_id}", response_model=UserResponse)
@log
async def get_user_by_id(
    user_id: int,
    admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
):
    """Get user by id"""
    return await user_service.get_user(user_id=user_id)


@router.post("/{user_id}/activate", response_model=UserResponse)
@log
async def deactivate_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
):
    """Activate user"""
    await user_service.activate_user(user_id=user_id)
    return JSONResponse(content=f"user {user_id} successfuly activated")


@router.post("/{user_id}/deactivate", response_model=UserResponse)
@log
async def deactivate_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    user_service: UserService = Depends(get_user_service),
):
    """Deactivate user"""
    await user_service.deactivate_user(user_id=user_id)
    return JSONResponse(content=f"user {user_id} successfuly deactivated")
