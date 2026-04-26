from typing import AsyncGenerator
import sys
import os

from unittest.mock import patch
import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base


# ============================================================
# TEST DB (SQLite in-memory)
# ============================================================


@pytest.fixture(scope="session")
def test_db_url():
    """
    URL for test DB — SQLite in memory.
    Do not required to install PostgreSQL.
    """
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_db_url):
    """
    Create test DB engine.
    scope="function" — new DB for every test.
    """
    engine = create_async_engine(
        url=test_db_url,
        echo=False,
        poolclass=StaticPool,  # One connection for all sessions
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Return test DB session.
    Automatically rolls back after each test — data is not persisted.
    """
    session_factory = async_sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


# ============================================================
# PATCHES
# ============================================================


@pytest.fixture(scope="session", autouse=True)
def patch_log():
    """
    Automatically patch the @log decorator to a no-op for all tests.
    Prevents logger I/O side-effects and speeds up test execution.
    """
    with patch("src.utils.logger.log", return_value=lambda func: func):
        yield


@pytest.fixture(scope="session", autouse=True)
def patch_log_database_queries():
    """
    Automatically patch the @log_database_queries decorator to a no-op for all tests.
    Prevents logger I/O side-effects and speeds up test execution.
    """
    with patch("src.utils.logger.log_database_queries", return_value=lambda func: func):
        yield


# ============================================================
# PLUGINS
# ============================================================

pytest_plugins = [
    "tests.fixtures.news",
    "tests.fixtures.user",
    "tests.fixtures.auth",
    "tests.fixtures.notification",
    "tests.fixtures.request",
]
