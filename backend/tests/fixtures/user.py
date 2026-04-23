from typing import AsyncGenerator, Callable, Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import User
from src.repositories import UserRepository
from src.services import UserService
from src.schemas.user import UserCreate, UserUpdate


# ============================================================
# MOCKS
# ============================================================


@pytest.fixture(scope="function")
def user_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for UserRepository.
    Pre-configures common methods to avoid repetitive setup in tests.
    """
    mock_repo = AsyncMock(spec=UserRepository)

    mock_repo.get_many.return_value = []
    mock_repo.get.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None

    return mock_repo


# ============================================================
# TEST DATA FACTORIES
# ============================================================


@pytest.fixture(scope="session")
def user_test_data_factory() -> Callable[..., Dict[str, Any]]:
    """
    Factory function to generate valid test data dictionaries for user entities.
    Returns a callable that accepts keyword overrides.
    """

    def _factory(**overrides: Any) -> Dict[str, Any]:
        base_data = {
            "id": 1,
            "title": "Test user Title",
            "content": "Test user content body",
            "author": "Test Author",
            "is_published": True,
        }
        base_data.update(overrides)
        return base_data

    return _factory


@pytest.fixture(scope="function")
def user_create_schema_factory(user_test_data_factory) -> Callable[..., UserCreate]:
    """
    Factory to create valid userCreate Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> UserCreate:
        data: Dict = user_test_data_factory(**overrides)
        data.pop("id", None)  # ID is usually auto-generated
        return UserCreate(**data)

    return _factory


# ============================================================
# SERVICE FIXTURES
# ============================================================


@pytest_asyncio.fixture(scope="function")
async def user_service_mocked(
    test_session, user_repository_mock
) -> AsyncGenerator[UserService, None]:
    """
    Instantiate userService with test_session and mocked repository.
    Ideal for pure unit tests isolating service logic from DB.
    """
    service = UserService(session=test_session, user_repository=user_repository_mock)
    yield service


@pytest_asyncio.fixture(scope="function")
async def user_service(test_session: AsyncSession) -> UserService:
    """
    Instantiate userService with real repository and test DB session.
    Ideal for integration tests verifying queries, pagination, and relations.
    """
    real_repo = UserRepository(User)
    return UserService(session=test_session, user_repository=real_repo)
