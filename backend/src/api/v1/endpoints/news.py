from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from api.dependencies import get_news_service, NewsService
from core.security import get_current_user, get_current_admin
from database import News, User
from schemas.news import NewsResponse, NewsUpdate
from utils.logger import log

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/", response_model=List[NewsResponse])
async def get_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
):
    """News list"""
    return await news_service.get_news_list(
        skip=skip, limit=limit, order_by=News.created_at
    )


@router.get("/last", response_model=NewsResponse)
async def get_last_news(
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
):
    """Get last news"""
    return await news_service.get_last_news()


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_by_id(
    news_id: int,
    current_user: User = Depends(get_current_user),
    news_service: NewsService = Depends(get_news_service),
):
    """News details"""
    return await news_service.get_news(news_id=news_id)
