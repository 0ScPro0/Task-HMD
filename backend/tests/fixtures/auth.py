from typing import AsyncGenerator, Callable, Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import User, UserRole
from src.repositories import UserRepository
from src.services import AuthService
from src.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenRefreshRequest,
)


# ============================================================
# TEST DATA FACTORIES
# ============================================================


@pytest.fixture(scope="function")
def register_request_schema_factory() -> Callable[..., RegisterRequest]:
    """
    Factory to create valid RegisterRequest Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> RegisterRequest:
        return RegisterRequest(**overrides)

    return _factory


@pytest.fixture(scope="function")
def login_request_schema_factory(
    user_test_data_factory,
) -> Callable[..., LoginRequest]:
    """
    Factory to create valid LoginRequest Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> LoginRequest:
        return LoginRequest(**overrides)

    return _factory


@pytest.fixture(scope="function")
def token_refresh_request_schema_factory(
    user_test_data_factory,
) -> Callable[..., TokenRefreshRequest]:
    """
    Factory to create valid TokenRefreshRequest Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> TokenRefreshRequest:
        return TokenRefreshRequest(**overrides)

    return _factory


# ============================================================
# SERVICE FIXTURES
# ============================================================


@pytest_asyncio.fixture(scope="function")
async def auth_service(test_session: AsyncSession) -> AuthService:
    """
    Instantiate AuthService with real repository and test DB session.
    Ideal for integration tests verifying queries, pagination, and relations.
    """
    repository = UserRepository(User)
    return AuthService(session=test_session, user_repository=repository)
