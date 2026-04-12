from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from api.dependencies import (
    get_request_service,
    get_notification_service,
    RequestService,
    NotificationService,
)
from core.security import get_current_user, get_current_admin
from core.exceptions import CreateError, PermissionDeniedError
from database import User, Request, UserRole
from schemas.request import RequestCreate, RequestBase, RequestResponse, RequestUpdate
from schemas.notification import NotificationCreate
from utils.logger import log

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("/create", response_model=RequestResponse)
async def create_request(
    request: RequestCreate,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Create request"""
    created_request = await request_service.create_request(request=request)

    # Create notification
    notification = await notification_service.create_notification(
        NotificationCreate(
            title=created_request.title,
            body=created_request.description,
            request_id=created_request.id,
            news_id=None,
        )
    )

    await notification_service.send_notifications(notification=notification)

    return RequestResponse.model_validate(created_request)


@router.get("/", response_model=List[RequestResponse])
async def get_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """List of requests"""
    return await request_service.get_requests(
        user=current_user, skip=skip, limit=limit, order_by=Request.id
    )


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Request details"""
    return await request_service.get_request(request_id=request_id, user=current_user)


@router.delete("/{request_id}", response_model=RequestResponse)
async def delete_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Delete request (only owner, executor or admin)"""
    return await request_service.delete_request(
        user_id=current_user.id, user_role=current_user.role, request_id=request_id
    )


@router.patch("/{request_id}/accept", response_model=RequestResponse)
async def executor_accept_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Executer accept specified request"""

    # Check user is not resident
    if current_user.role == UserRole.RESIDENT:
        raise PermissionDeniedError("Only executers can response to request")

    return await request_service.executor_accept_request(
        request_id=request_id, user=current_user, executor_id=current_user.id
    )


@router.patch("/{request_id}/status", response_model=RequestResponse)
async def update_request_status(
    request_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Change status (admin or worker)"""
    return await request_service.update_request_status(
        user_id=current_user.id,
        user_role=current_user.role,
        request_id=request_id,
        status=status,
    )
