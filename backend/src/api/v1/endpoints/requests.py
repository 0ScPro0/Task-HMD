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
@log
async def create_request(
    request: RequestCreate,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Create request"""
    return await request_service.create_request(request=request)


@router.get("/", response_model=List[RequestResponse])
@log
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


@router.get("/my", response_model=List[RequestResponse])
@log
async def get_user_requests(
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """List of user requests"""
    return await request_service.get_requests_by_user(user=current_user, limit=limit)


@router.get("/new", response_model=Optional[List[RequestResponse]])
@log
async def get_new_requests_by_user_role(
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """
    Get new requests for the role.
    Used only by executers
    """
    return await request_service.get_new_requests_by_role(
        role=current_user.role, limit=limit
    )


@router.get("/{request_id}", response_model=RequestResponse)
@log
async def get_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Request details"""
    return await request_service.get_request(request_id=request_id, user=current_user)


@router.delete("/{request_id}", response_model=RequestResponse)
@log
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
@log
async def executor_accept_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Executer accept specified request"""

    # Check user is not resident
    if current_user.role == UserRole.RESIDENT:
        raise PermissionDeniedError("Only executers can response to request")

    updated_request = await request_service.executor_accept_request(
        request_id=request_id, user=current_user, executor_id=current_user.id
    )

    # Create notification
    notification = await notification_service.create_notification(
        NotificationCreate(
            title="Отклик на заявку: " + updated_request.title,
            body=updated_request.description,
            request_id=updated_request.id,
            news_id=None,
        )
    )

    # Send notifications
    await notification_service.send_notifications(notification=notification)


@router.patch("/{request_id}/status", response_model=RequestResponse)
@log
async def update_request_status(
    request_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Change status (admin or worker)"""
    updated_request = await request_service.update_request_status(
        user_id=current_user.id,
        user_role=current_user.role,
        request_id=request_id,
        status=status,
    )

    # Create notification
    notification = await notification_service.create_notification(
        NotificationCreate(
            title="Изменение в заявке: " + updated_request.title,
            body=updated_request.description,
            request_id=updated_request.id,
            news_id=None,
        )
    )

    # Send notifications
    await notification_service.send_notifications(notification=notification)
