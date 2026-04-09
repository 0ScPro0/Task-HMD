from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_news_service, NewsService
from core.security import get_current_user, get_current_admin
from database import News, User
from schemas.news import NewsResponse, NewsUpdate
from utils.logger import log

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/news", response_model=NewsResponse)
async def create_news(
    admin: User = Depends(get_current_admin),
    news_service: NewsService = Depends(get_news_service),
):
    """Create news"""
    pass


@router.get("/news", response_model=NewsResponse)
async def get_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
):
    """News list"""
    pass


@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news_by_id(
    news_id: int,
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
):
    """News details"""
    pass


@router.patch("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    admin: User = Depends(get_current_admin),
    news_service: NewsService = Depends(get_news_service),
):
    """Update news"""
    pass


@router.delete("/news/{news_id}", response_model=NewsResponse)
async def delete_news(
    news_id: int,
    admin: User = Depends(get_current_admin),
    news_service: NewsService = Depends(get_news_service),
):
    """Delete news"""
    pass
