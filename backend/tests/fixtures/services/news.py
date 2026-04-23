from typing import AsyncGenerator, Callable, Dict, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import News
from src.repositories import NewsRepository
from src.services import NewsService
from src.schemas.news import NewsCreate


# ============================================================
# MOCKS
# ============================================================


@pytest.fixture(scope="function")
def news_repository_mock() -> AsyncMock:
    """
    Create an AsyncMock for NewsRepository.
    Pre-configures common methods to avoid repetitive setup in tests.
    """
    mock_repo = AsyncMock(spec=NewsRepository)

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
def news_test_data_factory() -> Callable[..., Dict[str, Any]]:
    """
    Factory function to generate valid test data dictionaries for News entities.
    Returns a callable that accepts keyword overrides.
    """

    def _factory(**overrides: Any) -> Dict[str, Any]:
        base_data = {
            "id": 1,
            "title": "Test News Title",
            "content": "Test news content body",
            "author": "Test Author",
            "is_published": True,
        }
        base_data.update(overrides)
        return base_data

    return _factory


@pytest.fixture(scope="function")
def news_create_schema_factory(news_test_data_factory) -> Callable[..., NewsCreate]:
    """
    Factory to create valid NewsCreate Pydantic schemas.
    Useful for testing service input validation and repository methods.
    """

    def _factory(**overrides: Any) -> NewsCreate:
        data = news_test_data_factory(**overrides)
        data.pop("id", None)  # ID is usually auto-generated
        return NewsCreate(**data)

    return _factory


# ============================================================
# SERVICE FIXTURES
# ============================================================


@pytest_asyncio.fixture(scope="function")
async def news_service_mocked(
    test_session, news_repository_mock
) -> AsyncGenerator[NewsService, None]:
    """
    Instantiate NewsService with test_session and mocked repository.
    Ideal for pure unit tests isolating service logic from DB.
    """
    service = NewsService(session=test_session, news_repository=news_repository_mock)
    yield service


@pytest_asyncio.fixture(scope="function")
async def news_service(test_session: AsyncSession) -> NewsService:
    """
    Instantiate NewsService with real repository and test DB session.
    Ideal for integration tests verifying queries, pagination, and relations.
    """
    real_repo = NewsRepository(News)
    return NewsService(session=test_session, news_repository=real_repo)
