from typing import AsyncGenerator, Callable, Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Request, RequestStatus, RequestType, User, UserRole
from src.repositories import RequestRepository
from src.services import RequestService
from src.schemas.request import (
    RequestCreate,
    RequestUpdate,
    RequestResponse,
)


# ============================================================
# MOCKS
# ============================================================


@pytest.fixture(scope="function")
def request_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for RequestRepository.
    Pre-configures common methods to avoid repetitive setup in tests.
    """
    mock_repo = AsyncMock(spec=RequestRepository)

    mock_repo.get_many.return_value = []
    mock_repo.get.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None
    mock_repo.get_requests_by_owner.return_value = []
    mock_repo.get_requests_by_role.return_value = []
    mock_repo.create_request.return_value = None
    mock_repo.update_request_executor.return_value = None
    mock_repo.update_request_executor_and_status.return_value = None
    mock_repo.update_request_status.return_value = None

    return mock_repo


# ============================================================
# TEST DATA FACTORIES
# ============================================================


@pytest.fixture(scope="session")
def request_test_data_factory() -> Callable[..., Dict[str, Any]]:
    """
    Factory function to generate valid test data dictionaries for request entities.
    Returns a callable that accepts keyword overrides.
    """

    def _factory(**overrides: Any) -> Dict[str, Any]:
        base_data = {
            "type": RequestType.ELECTRICIAN,
            "title": "Test Request",
            "description": "Test description",
            "status": RequestStatus.NEW,
            "admin_comment": None,
            "owner_id": 1,
            "executor_id": None,
        }
        base_data.update(overrides)
        return base_data

    return _factory


@pytest.fixture(scope="function")
def request_create_schema_factory(
    request_test_data_factory,
) -> Callable[..., RequestCreate]:
    """
    Factory to create valid RequestCreate Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> RequestCreate:
        data: Dict = request_test_data_factory(**overrides)
        # Ensure required fields are present
        return RequestCreate(**data)

    return _factory


@pytest.fixture(scope="function")
def request_update_schema_factory(
    request_test_data_factory,
) -> Callable[..., RequestUpdate]:
    """
    Factory to create valid RequestUpdate Pydantic schemas.
    """

    def _factory(**overrides: Any) -> RequestUpdate:
        data: Dict = request_test_data_factory(**overrides)
        return RequestUpdate(**data)

    return _factory


# ============================================================
# SERVICE FIXTURES
# ============================================================


@pytest_asyncio.fixture(scope="function")
async def request_service_mocked(
    test_session: AsyncSession,
    request_repository_mock: AsyncMock,
) -> AsyncGenerator[RequestService, None]:
    """
    Instantiate RequestService with test_session and mocked repository.
    Ideal for pure unit tests isolating service logic from DB.
    """
    service = RequestService(
        session=test_session,
        request_repository=request_repository_mock,
    )
    yield service


@pytest_asyncio.fixture(scope="function")
async def request_service(test_session: AsyncSession) -> RequestService:
    """
    Instantiate RequestService with real repository and test DB session.
    Ideal for integration tests verifying queries, pagination, and relations.
    """
    real_repo = RequestRepository(Request)
    return RequestService(session=test_session, request_repository=real_repo)
