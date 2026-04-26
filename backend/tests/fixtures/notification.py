from typing import AsyncGenerator, Callable, Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Notification, UserNotification, User, Request
from src.repositories import (
    NotificationRepository,
    UserNotificationRepository,
    UserRepository,
    RequestRepository,
)
from src.services import NotificationService
from src.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    FullNotificationResponse,
)
from src.schemas.user_notification import UserNotificationCreate


# ============================================================
# MOCKS
# ============================================================


@pytest.fixture(scope="function")
def notification_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for NotificationRepository.
    Pre-configures common methods to avoid repetitive setup in tests.
    """
    mock_repo = AsyncMock(spec=NotificationRepository)

    mock_repo.get_many.return_value = []
    mock_repo.get.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None
    mock_repo.create_notification.return_value = None

    return mock_repo


@pytest.fixture(scope="function")
def user_notification_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for UserNotificationRepository.
    """
    mock_repo = AsyncMock(spec=UserNotificationRepository)

    mock_repo.get_many.return_value = []
    mock_repo.get.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None
    mock_repo.get_user_notifications.return_value = []
    mock_repo.read_user_notification.return_value = None
    mock_repo.create_user_notification.return_value = None

    return mock_repo


@pytest.fixture(scope="function")
def user_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for UserRepository.
    """
    mock_repo = AsyncMock(spec=UserRepository)

    mock_repo.get_many.return_value = []
    mock_repo.get.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None

    return mock_repo


@pytest.fixture(scope="function")
def request_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for RequestRepository.
    """
    mock_repo = AsyncMock(spec=RequestRepository)

    mock_repo.get_many.return_value = []
    mock_repo.get.return_value = None
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None
    mock_repo.get_request.return_value = None

    return mock_repo


# ============================================================
# TEST DATA FACTORIES
# ============================================================


@pytest.fixture(scope="session")
def notification_test_data_factory() -> Callable[..., Dict[str, Any]]:
    """
    Factory function to generate valid test data dictionaries for notification entities.
    Returns a callable that accepts keyword overrides.
    """

    def _factory(**overrides: Any) -> Dict[str, Any]:
        base_data = {
            "title": "Test Notification",
            "body": "This is a test notification body.",
            "request_id": None,
            "news_id": None,
        }
        base_data.update(overrides)
        return base_data

    return _factory


@pytest.fixture(scope="function")
def notification_create_schema_factory(
    notification_test_data_factory,
) -> Callable[..., NotificationCreate]:
    """
    Factory to create valid NotificationCreate Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> NotificationCreate:
        data: Dict = notification_test_data_factory(**overrides)
        return NotificationCreate(**data)

    return _factory


@pytest.fixture(scope="function")
def notification_update_schema_factory(
    notification_test_data_factory,
) -> Callable[..., NotificationUpdate]:
    """
    Factory to create valid NotificationUpdate Pydantic schemas.
    """

    def _factory(**overrides: Any) -> NotificationUpdate:
        data: Dict = notification_test_data_factory(**overrides)
        return NotificationUpdate(**data)

    return _factory


# ============================================================
# SERVICE FIXTURES
# ============================================================


@pytest_asyncio.fixture(scope="function")
async def notification_service_mocked(
    test_session: AsyncSession,
    notification_repository_mock: AsyncMock,
    user_notification_repository_mock: AsyncMock,
    user_repository_mock: AsyncMock,
    request_repository_mock: AsyncMock,
) -> AsyncGenerator[NotificationService, None]:
    """
    Instantiate NotificationService with test_session and mocked repositories.
    Ideal for pure unit tests isolating service logic from DB.
    """
    service = NotificationService(
        session=test_session,
        notification_repository=notification_repository_mock,
        user_notification_repository=user_notification_repository_mock,
        user_repository=user_repository_mock,
        request_repository=request_repository_mock,
    )
    yield service


@pytest_asyncio.fixture(scope="function")
async def notification_service(test_session: AsyncSession) -> NotificationService:
    """
    Instantiate NotificationService with real repositories and test DB session.
    Ideal for integration tests verifying queries, pagination, and relations.
    """
    notification_repo = NotificationRepository(Notification)
    user_notification_repo = UserNotificationRepository(UserNotification)
    user_repo = UserRepository(User)
    request_repo = RequestRepository(Request)
    return NotificationService(
        session=test_session,
        notification_repository=notification_repo,
        user_notification_repository=user_notification_repo,
        user_repository=user_repo,
        request_repository=request_repo,
    )
