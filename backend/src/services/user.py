from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import NotFoundError
from database import User
from repositories import UserRepository
from schemas.user import UserCreate, UserResponse, UserUpdate
from services.base import BaseService
from utils.logger import log


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    """Service for working with User"""

    def __init__(self, session: AsyncSession, user_repository: UserRepository):
        super().__init__(
            repository=user_repository,
            session=session,
        )

    @log
    async def get_users(
        self,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        order_by: Optional[Any] = None,
    ) -> List[UserResponse]:
        users = await self.repository.get_many(
            self.session, skip=skip, limit=limit, order_by=order_by
        )
        if not users:
            raise NotFoundError("Not found any users")

        return [UserResponse.model_validate(user) for user in users]

    @log
    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.repository.get(self.session, user_id)
        if not user:
            raise NotFoundError("User not found")

        return UserResponse.model_validate(user)

    @log
    async def update_user(self, user_id: int, user: UserUpdate) -> UserResponse:
        updated_user = await self.repository.update(
            self.session, update_object_id=user_id, object_in=user
        )
        if not updated_user:
            raise NotFoundError("User not found")

        return UserResponse.model_validate(updated_user)

    @log
    async def delete_user(self, user_id: int) -> UserResponse:
        user = await self.repository.delete(self.session, id=user_id)
        if not user:
            raise NotFoundError("User not found")

        return UserResponse.model_validate(user)

    @log
    async def activate_user(self, user_id: int) -> UserResponse:
        user = await self.repository.activate(self.session, user_id=user_id)
        if not user:
            raise NotFoundError("User not found")

        return UserResponse.model_validate(user)

    @log
    async def deactivate_user(self, user_id: int) -> UserResponse:
        user = await self.repository.delete(self.session, id=user_id)
        if not user:
            raise NotFoundError("User not found")

        return UserResponse.model_validate(user)
