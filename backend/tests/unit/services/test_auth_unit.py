from typing import Dict, List

import sys

import pytest
from unittest.mock import MagicMock
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.database import User, UserRole
from src.services import AuthService, UserService
from schemas.auth import (  # type: ignore
    LoginRequest,  # type: ignore
    RegisterRequest,  # type: ignore
    LoginResponse,  # type: ignore
    RegisterResponse,  # type: ignore
    TokenRefreshRequest,  # type: ignore
    TokenRefreshResponse,  # type: ignore
)
from src.core.security import hash_password
from core.exceptions import NotFoundError, AuthError  # type: ignore
from src.utils.serializator import resolve_phone

# ============================================================
# INTEGRATION-STYLE TESTS (Real Repository + In-Memory DB)
# ============================================================
# Note: Logging is automatically patched via autouse fixture in conftest.


# ============================================================
# TESTS: registration
# ============================================================


@pytest.mark.asyncio
async def test_register_with_correct_data(
    auth_service: AuthService, register_request_schema_factory
) -> RegisterResponse:
    """Verify that user data correctly save in database."""
    register_request = register_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    response = await auth_service.register(request=register_request)

    assert response.user.email == register_request.email
    assert response.user.name == register_request.name
    assert response.user.surname == register_request.surname
    assert response.user.patronymic == register_request.patronymic
    assert response.user.address == register_request.address
    assert response.user.apartment == register_request.apartment
    assert response.user.phone == register_request.phone
    assert response.user.role == register_request.role
    assert response.access_token is not None  # Check token exists
    assert response.refresh_token is not None  # Check token exists

    return response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "phone,should_raise",
    [
        # Valid phones
        ("+79271234567", False),  # correct russian number
        ("79161234567", False),  # correct russian number without +
        ("89161234567", False),  # correct russian number starts with 8
        # Invalid phones
        ("+1234567890", True),  # incorrect country code
        ("+7927", True),  # too short
        ("+792712345678", True),  # too long
        ("invalid", True),  # is not a number
    ],
)
async def test_register_with_different_phones(
    phone: str,
    should_raise: bool,
    auth_service: AuthService,
    register_request_schema_factory,
):
    """Check the validity of different phone numbers"""

    if should_raise:
        with pytest.raises((ValidationError, AuthError)):
            register_request = register_request_schema_factory(
                email="test@example.com",
                name="Foo",
                surname="Bar",
                patronymic="Barovich",
                address="Walt st.",
                apartment="12",
                phone=phone,
                role=UserRole.RESIDENT,
                password="test_password",
            )

            await auth_service.register(request=register_request)

    else:
        register_request = register_request_schema_factory(
            email="test@example.com",
            name="Foo",
            surname="Bar",
            patronymic="Barovich",
            address="Walt st.",
            apartment="12",
            phone=phone,
            role=UserRole.RESIDENT,
            password="test_password",
        )

        response = await auth_service.register(request=register_request)

        assert response.user.phone == await resolve_phone(phone)


@pytest.mark.asyncio
async def test_register_check_same_password(
    test_session: AsyncSession,
    user_service: UserService,
    auth_service: AuthService,
    register_request_schema_factory,
):
    """
    Ensure that password hash is not dublicated with same passwords (salt applies correctly)
    """

    # Create RegisterRequest
    register_request = register_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    # Get RegisterResponse
    response = await auth_service.register(request=register_request)

    # Get User object from database
    user = await user_service.repository.get_user(
        test_session, user_id=response.user.id
    )

    # Password hashs must not be the same
    assert user.password_hash != hash_password("test_password")


# ============================================================
# TESTS: login
# ============================================================


@pytest.mark.asyncio
async def test_login_with_correct_data(
    auth_service: AuthService,
    user_create_schema_factory,
    register_request_schema_factory,
    login_request_schema_factory,
):
    """Verify that user can login with correct data"""

    # Register user
    register_request = register_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    register_response = await auth_service.register(request=register_request)

    # Login user
    login_request = login_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    login_response = await auth_service.login(login_request)

    assert login_response.user.id == register_response.user.id
    assert login_response.user.email == register_response.user.email
    assert login_response.user.name == register_response.user.name
    assert login_response.user.surname == register_response.user.surname
    assert login_response.user.patronymic == register_response.user.patronymic
    assert login_response.user.address == register_response.user.address
    assert login_response.user.apartment == register_response.user.apartment
    assert login_response.user.phone == register_response.user.phone
    assert login_response.user.role == register_response.user.role
    assert login_response.access_token is not None  # Check token exists
    assert login_response.refresh_token is not None  # Check token exists


# ============================================================
# TESTS: logout
# ============================================================


@pytest.mark.asyncio
async def test_logout(
    test_session: AsyncSession,
    user_service: UserService,
    auth_service: AuthService,
    register_request_schema_factory,
    login_request_schema_factory,
):
    """Verify that user can logout"""
    # Register user
    register_request = register_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    await auth_service.register(request=register_request)

    # Login user
    login_request = login_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )
    login_response = await auth_service.login(login_request)

    # Logout user
    assert await auth_service.logout(user_id=login_response.user.id) is True

    # Check that user do not have refresh token
    user = await user_service.repository.get_user(
        test_session, user_id=login_response.user.id
    )
    assert user.refresh_token is None


# ============================================================
# TESTS: get user from token
# ============================================================


@pytest.mark.asyncio
async def test_get_user_from_token_after_register(
    auth_service: AuthService,
    register_request_schema_factory,
):
    """Verify that user can get user from token"""

    # Register user
    register_request = register_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    register_response = await auth_service.register(request=register_request)

    # Get User object from token
    user = await auth_service.get_current_user(register_response.access_token)

    assert user.id == register_response.user.id


@pytest.mark.asyncio
async def test_get_user_from_token_after_login(
    auth_service: AuthService,
    register_request_schema_factory,
    login_request_schema_factory,
):
    """Verify that user can get user from token"""

    # Register user
    register_request = register_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )

    await auth_service.register(request=register_request)

    # Login user
    login_request = login_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="test_password",
    )
    login_response = await auth_service.login(login_request)

    # Get User object from token
    user = await auth_service.get_current_user(login_response.access_token)

    assert user.id == login_response.user.id


# ============================================================
# TESTS: refresh token
# ============================================================
