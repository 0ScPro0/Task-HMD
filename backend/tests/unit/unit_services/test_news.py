from typing import Dict, List

import sys

import pytest
from unittest.mock import MagicMock
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import News
from src.services import NewsService
from schemas.news import NewsResponse  # type: ignore
from core.exceptions import NotFoundError  # type: ignore


# ============================================================
# LOCAL FIXTURES & HELPERS
# ============================================================


@pytest.fixture(scope="function")
def mock_orm_news_factory():
    """
    Factory to generate mock SQLAlchemy ORM instances.
    Useful for pure unit tests where repository is mocked.
    """

    def _factory(**overrides: dict) -> MagicMock:
        base_attrs = {
            "id": 1,
            "title": "Default Title",
            "content": "Default Content",
            "author": "Default Author",
            "is_published": True,
            "created_at": "2026-01-01T00:00:00",
        }
        base_attrs.update(overrides)

        mock = MagicMock()
        for attr, value in base_attrs.items():
            setattr(mock, attr, value)
        return mock

    return _factory


# ============================================================
# INTEGRATION-STYLE TESTS (Real Repository + In-Memory DB)
# ============================================================
# Note: Logging is automatically patched via autouse fixture in conftest.


@pytest.mark.asyncio
async def test_get_news_list_initially_empty(
    news_service: NewsService, test_session: AsyncSession
):
    """Verify service returns empty list when database contains no records."""
    result = await news_service.get_news_list()
    assert result == []
    assert len(test_session.new) == 0  # SQLAlchemy identity map check


@pytest.mark.asyncio
async def test_get_news_list_retrieves_created_items(
    news_service: NewsService, test_session: AsyncSession, news_create_schema_factory
):
    """Ensure service correctly fetches and maps records inserted via repository."""
    await news_service.repository.create_news(
        test_session,
        news_object=news_create_schema_factory(
            title="Alpha", content="Alpha", is_published=False
        ),
    )
    await news_service.repository.create_news(
        test_session,
        news_object=news_create_schema_factory(
            title="Beta", content="Beta", is_published=True
        ),
    )
    await test_session.commit()

    result = await news_service.get_news_list()
    assert len(result) == 2
    assert {item.title for item in result} == {"Alpha", "Beta"}
    assert all(isinstance(item, NewsResponse) for item in result)


@pytest.mark.asyncio
async def test_get_news_list_applies_pagination(
    news_service: NewsService, test_session: AsyncSession, news_create_schema_factory
):
    """Validate that skip and limit parameters correctly slice the dataset."""
    for i in range(5):
        await news_service.repository.create_news(
            test_session,
            news_object=news_create_schema_factory(
                title=f"News_{i}", content=f"News_{i}", is_published=False
            ),
        )
    await test_session.commit()

    result = await news_service.get_news_list(skip=2, limit=2)
    assert len(result) == 2
    titles = [item.title for item in result]
    assert "News_0" not in titles
    assert "News_1" not in titles


@pytest.mark.asyncio
async def test_get_news_list_respects_ordering(
    news_service: NewsService, test_session: AsyncSession, news_create_schema_factory
):
    """Confirm order_by clause is propagated to SQL query and results are sorted."""
    await news_service.repository.create_news(
        test_session,
        news_object=news_create_schema_factory(
            title="Zeta", content="Zeta", is_published=False
        ),
    )
    await news_service.repository.create_news(
        test_session,
        news_object=news_create_schema_factory(
            title="Alpha", content="Alpha", is_published=True
        ),
    )
    await test_session.commit()

    result: List[NewsResponse] = await news_service.get_news_list()

    assert result[0].title == "Zeta"
    assert result[0].content == "Zeta"
    assert result[0].is_published == False
    assert result[1].title == "Alpha"
    assert result[1].content == "Alpha"
    assert result[1].is_published == True


# ============================================================
# TESTS: get_news
# ============================================================


@pytest.mark.asyncio
async def test_get_news_existing_returns_valid_response(
    news_service: NewsService,
    test_session: AsyncSession,
    news_create_schema_factory,
):
    """Fetch single record by ID and verify schema serialization."""
    await news_service.repository.create_news(
        test_session, news_object=news_create_schema_factory(title="Single Record")
    )
    await test_session.commit()

    # Retrieve ID from freshly created record
    created_id = (await news_service.get_news_list())[0].id
    result = await news_service.get_news(created_id)

    assert result.id == created_id
    assert result.title == "Single Record"
    assert isinstance(result, NewsResponse)


@pytest.mark.asyncio
async def test_get_news_nonexistent_raises_not_found(news_service: NewsService):
    with pytest.raises(NotFoundError):
        await news_service.get_news(9999)
