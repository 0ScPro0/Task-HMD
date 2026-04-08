from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from repositories.base import BaseRepository
from database import News
from schemas.news import NewsCreate, NewsUpdate

from utils.logger import log_database_queries


class NewsRepository(BaseRepository[News, NewsCreate, NewsUpdate]):
    """Class for News specific News operations"""

    async def get_news(self, session: AsyncSession, *, news_id: int) -> Optional[News]:
        """
        Get News by id

        Args:
            session: Database session
            News_id: Specific News id

        Returns:
            News or None if not found
        """
        news = await self.get(session, id=news_id)
        return news

    async def create_news(
        self, session: AsyncSession, *, news_object: Union[NewsCreate, Dict[str, Any]]
    ) -> News:
        """
        Create News

        Args:
            session: Database session
            News_object: NewsCreate object or dict

        Returns:
            Created News object
        """
        news = await self.create(session=session, object_in=news_object)
        return news
