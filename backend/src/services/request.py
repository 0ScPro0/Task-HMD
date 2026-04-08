from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from database import Request
from repositories import RequestRepository
from schemas.request import RequestCreate, RequestUpdate, RequestResponse
from services.base import BaseService
from utils.logger import log


class RequestService(
    BaseService[Request, RequestCreate, RequestUpdate, RequestRepository]
):
    """Service for working with Request"""

    def __init__(self, session: AsyncSession, request_repository: RequestRepository):
        super().__init__(
            repository=request_repository,
            session=session,
        )

    @log
    async def get_all_requests(self) -> List[RequestResponse]:
        requests = await self.repository.get_many(
            self.session, skip=0, limit=100, order_by=None
        )
        return [RequestResponse.model_validate(request) for request in requests]

    @log
    async def get_request(self, request_id: int) -> RequestResponse:
        request = await self.repository.get(self.session, request_id)
        return RequestResponse.model_validate(request)

    @log
    async def update_request(
        self, request_id: int, request: RequestUpdate
    ) -> RequestResponse:
        request = await self.repository.update(self.session, request_id, request)
        return RequestResponse.model_validate(request)

    @log
    async def delete_request(self, request_id: int) -> RequestResponse:
        request = await self.repository.delete(self.session, request_id)
        return RequestResponse.model_validate(request)
