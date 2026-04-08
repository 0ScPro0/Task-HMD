from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from database import User
from repositories import UserRepository
from schemas.user import UserCreate, UserResponse
from schemas.user import UserCreate, UserUpdate
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
    async def get_all_users(self) -> List[UserResponse]:
        users = await self.repository.get_many(
            self.session, skip=0, limit=100, order_by=None
        )
        return [UserResponse.model_validate(user) for user in users]

    @log
    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.repository.get(self.session, user_id)
        return UserResponse.model_validate(user)

    @log
    async def update_user(self, user_id: int, user: UserUpdate) -> UserResponse:
        user = await self.repository.update(self.session, user_id, user)
        return UserResponse.model_validate(user)

    @log
    async def delete_user(self, user_id: int) -> UserResponse:
        user = await self.repository.delete(self.session, user_id)
        return UserResponse.model_validate(user)
