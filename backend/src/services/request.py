from typing import Any, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError, BadRequestError, PermissionDeniedError
from database import Request, RequestStatus, RequestType, User, UserRole
from repositories import RequestRepository
from schemas.request import RequestCreate, RequestUpdate, RequestResponse
from services.base import BaseService
from utils.logger import log, logger


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
        if not self._is_admin(user):
            raise PermissionDeniedError("Not enough permissions")

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
        requests = await self.repository.get_requests_by_owner(
            self.session, owner_id=user.id, limit=limit
        )
        if not requests:
            raise NotFoundError("User has not any requests")
        return [RequestResponse.model_validate(request) for request in requests]

    @log
    async def get_new_requests_by_executor_role(
        self,
        executor: User,
        limit: Optional[int] = 100,
    ) -> Optional[List[RequestResponse]]:
        """
        Get new requests for the role.
        Used only by executers.

        Args:
            user_id: User id
            limit: Number of requests to return

        Returns:
            List of RequestResponse
        """
        if not self._is_executor(executor) and not self._is_admin(executor):
            raise PermissionDeniedError("Not enough permissions")

        requests = await self.repository.get_requests_by_role(
            self.session, role=executor.role, limit=limit, status=RequestStatus.NEW
        )
        if not requests:
            return []
        return [RequestResponse.model_validate(request) for request in requests]

    @log
    async def get_request(
        self,
        user: User,
        request_id: int,
    ) -> RequestResponse:
        request = await self.repository.get(self.session, id=request_id)
        if not request:
            raise NotFoundError("Request not found")

        # Admin -> all
        if self._is_admin(user):
            return RequestResponse.model_validate(request)

        # Executor (by role)
        if self._is_executor(user):
            # NEW request -> check if new
            if request.status == RequestStatus.NEW:
                if not self._is_request_type_executor_role(user, request):
                    raise PermissionDeniedError("Not enough permissions")
            # Not NEW → executor must be appointed
            else:
                if not self._is_request_executor(user, request):
                    raise PermissionDeniedError("Not enough permissions")
            return RequestResponse.model_validate(request)

        # Resident → only his own requests
        if self._is_resident(user):
            if not self._is_request_owner(user, request):
                raise PermissionDeniedError("Not enough permissions")
            return RequestResponse.model_validate(request)

        raise PermissionDeniedError("Not enough permissions")

    @log
    async def create_request(self, request: RequestCreate) -> Request:
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
            raise BadRequestError("Request was not created")
        return created_request

    @log
    async def update_request(
        self, user: User, request_id: int, data: RequestUpdate
    ) -> RequestResponse:
        """
        Update request

        Args:
            request_id: Request id
            request: RequestUpdate

        Returns:
            RequestResponse
        """
        current_request = await self.repository.get_request(
            self.session, request_id=request_id
        )
        if not current_request:
            raise NotFoundError("Request not found")

        # Check user is admin
        if not self._is_admin(user):
            # Check user is executor of the request
            if not self._is_request_executor(user, current_request):
                # Check user is owner of the request
                if not self._is_request_owner(user, current_request):
                    raise PermissionDeniedError("Not enough permissions")

        updated_request = await self.repository.update(
            self.session, update_object_id=request_id, object_in=data
        )
        if not current_request:
            raise NotFoundError("Request not found")

        return RequestResponse.model_validate(updated_request)

    @log
    async def executor_accept_request(
        self, request_id: int, executor: User
    ) -> RequestResponse:
        """
        Update request executor

        Args:
            request_id: Request id
            executor_id: Executor id

        Returns:
            RequestResponse
        """
        request = await self.get_request(request_id=request_id, user=executor)
        if not request:
            raise NotFoundError("Request not found")

        # Check user is admin
        if not self._is_admin(executor):

            # Check request.type == executor.role
            if not self._is_request_type_executor_role(executor, request):
                raise PermissionDeniedError("Not enough permissions")

            # Check executor does not respond to his own request
            if self._is_request_owner(executor, request):
                raise PermissionDeniedError("Can not respond to your own requests")

        # Check if the status needs to be changed to in_progress
        if self._compare_request_status(request, RequestStatus.NEW):
            updated_request = await self.repository.update_request_executor_and_status(
                self.session,
                request_id=request_id,
                executor_id=executor.id,
                status=RequestStatus.IN_PROGRESS,
            )
        else:
            raise PermissionDeniedError("Request is already accepted")
        return RequestResponse.model_validate(updated_request)

    @log
    async def update_request_status(
        self, user: User, request_id: int, status: str
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
        request = await self.repository.get(self.session, id=request_id)
        if not request:
            raise NotFoundError("Request not found")

        # Check user is admin or request executor
        if not self._is_admin(user) and not self._is_request_executor(user, request):
            raise PermissionDeniedError(
                "Only admin or request executer can change request status"
            )

        request = await self.repository.update_request_status(
            self.session, request_id=request_id, status=status
        )
        return RequestResponse.model_validate(request)

    @log
    async def delete_request(self, user: User, request_id: int) -> bool:
        """
        Delete request

        Args:
            user_id: User id
            request_id: Request id

        Raises:
            NotFoundError: If request not found
            PermissionDeniedError: If user is not admin, request owner or executor

        Returns:
            True if request was deleted, raise NotFoundError otherwise
        """
        # Get request
        request = await self.repository.get(self.session, id=request_id)
        if not request:
            raise NotFoundError("Request not found")

        # Check user is admin
        if not self._is_admin(user):
            # Check user is executor of the request
            if not self._is_request_executor(user, request):
                # Check user is owner of the request
                if not self._is_request_owner(user, request):
                    raise PermissionDeniedError("Not enough permissions")

        deleted_request = await self.repository.delete(self.session, id=request_id)
        if not deleted_request:
            raise NotFoundError("Request not found")
        return True

    def _compare_request_status(
        self, request: Request, status: Union[str, RequestStatus]
    ) -> bool:
        """
        Compare request status with the submitted status

        Args:
            request: Request

        Returns:
            bool
        """
        if isinstance(status, RequestStatus):
            status = status.value

        return request.status.value == status

    def _compare_user_role(self, user: User, role: Union[str, UserRole]) -> bool:
        """
        Compare user role with the submitted role

        Args:
            user: User

        Returns:
            bool
        """
        if isinstance(role, UserRole):
            role = role.value

        return user.role.value == role

    def _is_request_owner(self, user: User, request: Request) -> bool:
        """
        Check if user is the request owner

        Args:
            request: Request

        Returns:
            bool
        """
        return request.owner_id == user.id

    def _is_request_executor(self, executor: User, request: Request) -> bool:
        """
        Check if user is the request executor

        Args:
            request: Request

        Returns:
            bool
        """
        return request.executor_id == executor.id

    def _is_resident(self, user: User) -> bool:
        """
        Check if user is the request owner

        Args:
            request: Request

        Returns:
            bool
        """
        return user.role.value == UserRole.RESIDENT.value

    def _is_executor(self, executor: User) -> bool:
        """
        Check if user is the request executor

        Args:
            request: Request

        Returns:
            bool
        """
        return executor.role.value in [
            UserRole.PLUMBER.value,
            UserRole.ELECTRICIAN.value,
        ]

    def _is_admin(self, user: User) -> bool:
        """
        Check if user is the admin

        Args:
            request: Request

        Returns:
            bool
        """
        return user.role.value == UserRole.ADMIN.value

    def _is_request_type_executor_role(self, executor: User, request: Request) -> bool:
        """
        Check if request type is the same as the executor role

        Args:
            request: Request

        Returns:
            bool
        """
        return request.type.value == executor.role.value
