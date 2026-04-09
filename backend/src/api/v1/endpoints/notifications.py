from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_notification_service, NotificationService
from core.security import get_current_user
from database import Notification
from schemas.notification import NotificationResponse
from utils.logger import log

router = APIRouter(prefix="/notifications", tags=["notifications"])
