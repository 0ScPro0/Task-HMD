from typing import Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError, CreateError, PermissionDeniedError
from database import Request, RequestStatus, User, UserRole
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
    async def get_requests(
        self,
        user: User,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        order_by: Optional[Any] = None,
    ) -> List[RequestResponse]:
        """
        Get all requests

        Args:
            skip: Number of requests to skip
            limit: Number of requests to return
            order_by: Field to order by

        Returns:
            List of requests
        """
        if user.role != UserRole.ADMIN:
            PermissionDeniedError("Only admin can get")
        requests = await self.repository.get_many(
            self.session, skip=skip, limit=limit, order_by=order_by
        )
        if not requests:
            raise NotFoundError("Not found any requests")
        return [RequestResponse.model_validate(request) for request in requests]

    @log
    async def get_requests_by_user(
        self,
        user: User,
        limit: Optional[int] = 100,
    ) -> List[RequestResponse]:
        """
        Get requests by user

        Args:
            user_id: User id
            limit: Number of requests to return

        Returns:
            List of RequestResponse
        """
        requests = await self.repository.get_requests_by_user(
            self.session, user_id=user.id, limit=limit
        )
        if not requests:
            raise NotFoundError("User has not any requests")
        return [RequestResponse.model_validate(request) for request in requests]

    @log
    async def get_request(
        self,
        user: User,
        request_id: int,
    ) -> RequestResponse:
        """
        Get request by id

        Args:
            request_id: Request id

        Returns:
            RequestResponse
        """
        request: Request = await self.repository.get(self.session, id=request_id)
        if not request:
            raise NotFoundError("Request not found")
        if (
            user.role != UserRole.ADMIN
            or request.owner_id != user.id
            or request.executor_id != user.id
        ):
            raise PermissionDeniedError("Only admin, owner or executor can get request")
        return RequestResponse.model_validate(request)

    @log
    async def create_request(self, request: RequestCreate) -> RequestResponse:
        """
        Create request

        Args:
            request: RequestCreate

        Returns:
            RequestResponse
        """
        created_request = await self.repository.create_request(
            self.session, request_object=request
        )
        if not created_request:
            raise CreateError("Request was not created")
        return RequestResponse.model_validate(created_request)

    @log
    async def update_request(
        self, request_id: int, request: RequestUpdate
    ) -> RequestResponse:
        """
        Update request

        Args:
            request_id: Request id
            request: RequestUpdate

        Returns:
            RequestResponse
        """
        request = await self.repository.update(self.session, request_id, request)
        if not request:
            raise NotFoundError("Request not found")
        return RequestResponse.model_validate(request)

    @log
    async def update_request_executor(
        self, request_id: int, user: User, executor_id: int
    ) -> RequestResponse:
        """
        Update request executor

        Args:
            request_id: Request id
            executor_id: Executor id

        Returns:
            RequestResponse
        """
        request = await self.get_request(request_id=request_id, user=user.id)
        if not request:
            raise NotFoundError("Request not found")

        # Check user is admin or request executor with same role
        if user.role != UserRole.ADMIN or request.type != user.role:
            raise PermissionDeniedError(
                "Only admin or executer with same role can update request executer"
            )

        # Check if the status needs to be changed to in_progress
        if request.status == RequestStatus.NEW:
            updated_request = await self.repository.update_request_executor_and_status(
                self.session,
                request_id=request_id,
                executor_id=executor_id,
                status=RequestStatus.IN_PROGRESS,
            )
        else:
            updated_request = await self.repository.update_request_executor(
                self.session, request_id=request_id, executor_id=executor_id
            )
        return RequestResponse.model_validate(updated_request)

    @log
    async def update_request_status(
        self, user_id: int, user_role: str, request_id: int, status: str
    ) -> RequestResponse:
        """
        Update request status

        Args:
            request_id: Request id
            status: Request status

        Returns:
            RequestResponse
        """
        # Get request
        request: Request = await self.repository.get(self.session, id=request_id)
        if not request:
            raise NotFoundError("Request not found")

        # Check user is admin or request executor
        if user_role != UserRole.ADMIN or request.executor_id != user_id:
            raise PermissionDeniedError(
                "Only admin or request executer can change request status"
            )

        request = await self.repository.update_request_status(
            self.session, request_id=request_id, status=status
        )
        return RequestResponse.model_validate(request)

    @log
    async def delete_request(
        self, user_id: int, user_role: str, request_id: int
    ) -> bool:
        """
        Delete request

        Args:
            user_id: User id
            request_id: Request id

        Returns:
            True if request was deleted else False
        """
        # Get request
        request: Request = await self.repository.get(self.session, id=request_id)
        if not request:
            raise NotFoundError("Request not found")

        # Check user is admin, request owner or executor
        if (
            user_role != UserRole.ADMIN
            or request.owner_id != user_id
            or request.executor_id != user_id
        ):
            raise PermissionDeniedError(
                "Only admin, worker or request owner can delete request"
            )

        deleted_request = await self.repository.delete(self.session, request_id)
        return True
