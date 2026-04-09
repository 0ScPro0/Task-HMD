from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_request_service, RequestService
from core.security import get_current_user, get_current_admin
from database import User, Request
from schemas.request import RequestCreate, RequestBase, RequestResponse, RequestUpdate
from utils.logger import log

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("/requests", response_model=RequestResponse)
async def create_request(
    request: RequestCreate,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Create request"""
    pass


@router.get("/requests", response_model=RequestResponse)
async def get_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    request_status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """List of requests (filter by status, type)"""
    pass


@router.get("/requests/{request_id}", response_model=RequestResponse)
async def get_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Request details"""
    pass


@router.patch("/requests/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Update request (text only)"""
    pass


@router.delete("/requests/{request_id}", response_model=RequestResponse)
async def delete_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Delete request (only owner, worker or admin)"""
    pass


@router.patch("/requests/{request_id}/status", response_model=RequestResponse)
async def update_request_status(
    request_id: int,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service),
):
    """Change status (admin or worker)"""
    pass
