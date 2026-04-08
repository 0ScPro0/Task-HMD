from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from repositories.base import BaseRepository
from database import Request
from schemas.request import RequestCreate, RequestUpdate

from utils.logger import log_database_queries


class RequestRepository(BaseRepository[Request, RequestCreate, RequestUpdate]):
    """Class for request specific Request operations"""

    async def get_request(
        self, session: AsyncSession, *, request_id: int
    ) -> Optional[Request]:
        """
        Get Request by id

        Args:
            session: Database session
            request_id: Specific request id

        Returns:
            Request or None if not found
        """
        request = await self.get(session, id=request_id)
        return request

    async def create_request(
        self,
        session: AsyncSession,
        *,
        request_object: Union[RequestCreate, Dict[str, Any]]
    ) -> Request:
        """
        Create Request

        Args:
            session: Database session
            request_object: requestCreate object or dict

        Returns:
            Created Request object
        """
        request = await self.create(session=session, object_in=request_object)
        return request


request_repository = RequestRepository(Request)
