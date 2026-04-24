from typing import Dict, List

import sys

import pytest
from unittest.mock import MagicMock
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import User, UserRole
from src.services import UserService
from src.schemas.user import UserUpdate, UserUpdatePassword
from schemas.user import UserResponse  # type: ignore
from core.exceptions import NotFoundError  # type: ignore

# ============================================================
# INTEGRATION-STYLE TESTS (Real Repository + In-Memory DB)
# ============================================================
# Note: Logging is automatically patched via autouse fixture in conftest.


# ============================================================
# TESTS: get_user
# ============================================================


@pytest.mark.asyncio
async def test_get_user_list_initially_empty(
    user_service: UserService, test_session: AsyncSession
):
    """Verify service returns empty list when database contains no records."""
    with pytest.raises(NotFoundError):
        await user_service.get_users()


@pytest.mark.asyncio
async def test_get_user_list_retrieves_created_items(
    user_service: UserService, test_session: AsyncSession, user_create_schema_factory
):
    """Ensure service correctly fetches and maps records inserted via repository."""
    await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="test1email@example.com",
            name="Test1",
            surname="Test1",
            phone="+79999999991",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="test2email@example.com",
            name="Test2",
            surname="Test2",
            phone="+79999999992",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    result = await user_service.get_users()
    assert len(result) == 2
    assert {item.name for item in result} == {"Test1", "Test2"}
    assert all(isinstance(item, UserResponse) for item in result)


@pytest.mark.asyncio
async def test_get_user_list_applies_pagination(
    user_service: UserService, test_session: AsyncSession, user_create_schema_factory
):
    """Validate that skip and limit parameters correctly slice the dataset."""
    for i in range(5):
        await user_service.repository.create_user(
            test_session,
            user_object=user_create_schema_factory(
                email=f"test{i}email@example.com",
                name=f"user_{i}",
                surname=f"user_{i}",
                phone=f"+7999999999{i}",
                role=UserRole.RESIDENT,
                password_hash="very_secure_password",
            ),
        )
    await test_session.commit()

    result = await user_service.get_users(skip=2, limit=2)
    assert len(result) == 2
    titles = [item.name for item in result]
    assert "user_0" not in titles
    assert "user_1" not in titles


@pytest.mark.asyncio
async def test_get_user_list_respects_ordering(
    user_service: UserService, test_session: AsyncSession, user_create_schema_factory
):
    """Confirm order_by clause is propagated to SQL query and results are sorted."""
    await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="test1email@example.com",
            name="Test1",
            surname="Test1",
            phone="+79999999991",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="test2email@example.com",
            name="Test2",
            surname="Test2",
            phone="+79999999992",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    result: List[UserResponse] = await user_service.get_users()

    assert result[0].name == "Test1"
    assert result[1].name == "Test2"


@pytest.mark.asyncio
async def test_get_user_existing_returns_valid_response(
    user_service: UserService,
    test_session: AsyncSession,
    user_create_schema_factory,
):
    """Fetch single record by ID and verify schema serialization."""
    await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="testemail@example.com",
            name="Test",
            surname="Test",
            phone="+79999999999",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    # Retrieve ID from freshly created record
    created_id = (await user_service.get_users())[0].id
    result = await user_service.get_user(created_id)

    assert result.id == created_id
    assert result.name == "Test"
    assert isinstance(result, UserResponse)


@pytest.mark.asyncio
async def test_get_user_nonexistent_raises_not_found(user_service: UserService):
    with pytest.raises(NotFoundError):
        await user_service.get_user(9999)


# ============================================================
# TESTS: update_user
# ============================================================


@pytest.mark.asyncio
async def test_update_user_data(
    user_service: UserService,
    test_session: AsyncSession,
    user_create_schema_factory,
    user_update_schema_factory,
):
    """Verify that user fields are correctly updated and returned."""
    # Create initial user
    created_user = await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="old@example.com",
            name="OldName",
            surname="OldSurname",
            phone="+79990000000",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    # Prepare update data
    update_data = user_update_schema_factory(
        name="NewName",
        surname="NewSurname",
        phone="+79991111111",
        role=UserRole.PLUMBER,
    )

    # Perform update
    result = await user_service.update_user(user_id=created_user.id, user=update_data)

    # Assertions
    assert isinstance(result, UserResponse)
    assert result.id == created_user.id
    assert result.name == "NewName"
    assert result.surname == "NewSurname"
    assert result.phone == "+79991111111"
    assert result.role == UserRole.PLUMBER
    # Email and role should remain unchanged if not provided in update
    assert result.email == "old@example.com"


@pytest.mark.asyncio
async def test_activate_user(
    user_service: UserService, test_session: AsyncSession, user_create_schema_factory
):
    # Create initial user
    created_user = await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="old@example.com",
            name="OldName",
            surname="OldSurname",
            phone="+79990000000",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    updated_user = await user_service.repository.activate(
        test_session, user_id=created_user.id
    )

    assert updated_user.is_active == True


@pytest.mark.asyncio
async def test_deactivate_user(
    user_service: UserService, test_session: AsyncSession, user_create_schema_factory
):
    # Create initial user
    created_user = await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="old@example.com",
            name="OldName",
            surname="OldSurname",
            phone="+79990000000",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    updated_user = await user_service.repository.deactivate(
        test_session, user_id=created_user.id
    )

    assert updated_user.is_active == False


@pytest.mark.asyncio
async def test_update_nonexistent_user_raises_not_found(
    user_service: UserService, user_update_schema_factory
):
    """Ensure NotFoundError is raised when trying to update a missing user."""
    update_data = user_update_schema_factory(
        name="Nobody", surname="Nobody", phone="+79999999999", role=UserRole.RESIDENT
    )

    with pytest.raises(NotFoundError, match="User not found"):
        await user_service.update_user(user_id=9999, user=update_data)


# ============================================================
# TESTS: delete_user
# ============================================================


@pytest.mark.asyncio
async def test_delete_user(
    user_service: UserService, test_session: AsyncSession, user_create_schema_factory
):
    # Create initial user
    created_user = await user_service.repository.create_user(
        test_session,
        user_object=user_create_schema_factory(
            email="test@example.com",
            name="Test",
            surname="Test",
            phone="+79990000000",
            role=UserRole.RESIDENT,
            password_hash="very_secure_password",
        ),
    )
    await test_session.commit()

    deleted_user = await user_service.delete_user(user_id=created_user.id)

    with pytest.raises(NotFoundError, match="User not found"):
        await user_service.get_user(user_id=deleted_user.id)


@pytest.mark.asyncio
async def test_delete_nonexistent_user_raises_not_found(user_service: UserService):
    """Ensure NotFoundError is raised when trying to delete a missing user."""
    with pytest.raises(NotFoundError, match="User not found"):
        await user_service.delete_user(
            user_id=9999,
        )
