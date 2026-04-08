from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from database import News
from repositories import NewsRepository
from schemas.news import NewsCreate, NewsUpdate, NewsResponse
from services.base import BaseService
from utils.logger import log


class NewsService(BaseService[News, NewsCreate, NewsUpdate, NewsRepository]):
    """Service for working with News"""

    def __init__(self, session: AsyncSession, news_repository: NewsRepository):
        super().__init__(
            repository=news_repository,
            session=session,
        )

    @log
    async def get_all_news(self) -> List[NewsResponse]:
        news_list = await self.repository.get_many(
            self.session, skip=0, limit=100, order_by=None
        )
        return [NewsResponse.model_validate(news) for news in news_list]

    @log
    async def get_news(self, news_id: int) -> NewsResponse:
        news = await self.repository.get(self.session, news_id)
        return NewsResponse.model_validate(news)

    @log
    async def update_news(self, news_id: int, news: NewsUpdate) -> NewsResponse:
        news = await self.repository.update(self.session, news_id, news)
        return NewsResponse.model_validate(news)

    @log
    async def delete_news(self, news_id: int) -> NewsResponse:
        news = await self.repository.delete(self.session, news_id)
        return NewsResponse.model_validate(news)
