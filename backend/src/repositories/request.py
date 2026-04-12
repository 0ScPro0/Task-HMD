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

    async def get_requests_by_user(
        self, session: AsyncSession, *, user_id: int, limit: Optional[int] = 100
    ) -> Optional[List[Request]]:
        """
        Get Requests list by user id

        Args:
            session: Database session
            user_id: Specific user id
            limit: Limit of entry

        Returns:
            List of requests or None if not found
        """
        requests = await self.get_by_field_many(
            session, field_name="user_id", field_value=user_id, limit=limit
        )
        return requests

    async def get_request_status(self, session: AsyncSession, request_id: int) -> str:
        """
        Get Request status

        Args:
            session: Database session
            request_id: Specific request id

        Returns:
            Request status
        """
        request = await self.get_request(session, request_id=request_id)
        return request.status

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

    async def update_request_executor(
        self, session: AsyncSession, request_id: int, executor_id: int
    ) -> Optional[Request]:
        """
        Update Request executor

        Args:
            session: Database session
            request_id: Specific request id
            executor_id: Specific executor id

        Returns:
            Updated Request object
        """
        updated_request = await self.update_field(
            session,
            object_id=request_id,
            field_name="executor_id",
            field_value=executor_id,
        )
        return updated_request

    async def update_request_status(
        self, session: AsyncSession, *, request_id: int, status: str
    ) -> Optional[Request]:
        """
        Update Request status

        Args:
            session: Database session
            request_id: Specific request id
            status: New status

        Returns:
            Updated Request object
        """
        updated_request = await self.update_field(
            session, object_id=request_id, field_name="status", field_value=status
        )
        return updated_request

    async def update_request_executor_and_status(
        self, session: AsyncSession, request_id: int, executor_id: int, status: str
    ) -> Optional[Request]:
        """
        Update Request executor and status

        Args:
            session: Database session
            request_id: Specific request id
            executor_id: Specific executor id
            status: Request status

        Returns:
            Updated Request object
        """
        fields = {"executor_id": executor_id, "status": status}
        updated_request = await self.update_fields(
            session,
            object_id=request_id,
            fields=fields,
        )
        return updated_request

    async def is_request_has_executor(
        self, session: AsyncSession, *, request_id: int
    ) -> Optional[bool]:
        """
        Check request has executor

        Args:
            session: Database session
            request_id: Specific request id

        Returns:
            True if request has executor, else False or None if request is not found.
        """
        request = await self.get_request(session, request_id=request_id)
        if not request:
            return None
        return True if request.executor_id else False


request_repository = RequestRepository(Request)
