from typing import Dict, List
import asyncio
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
from src.core.security import hash_password, decode_token
from core.exceptions import NotFoundError, AuthError, PermissionDeniedError  # type: ignore
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
    "phone",
    [
        ("+79271234567"),  # correct russian number
        ("79161234567"),  # correct russian number without +
        ("89161234567"),  # correct russian number starts with 8
    ],
)
async def test_register_with_correct_phones(
    phone: str,
    auth_service: AuthService,
    register_request_schema_factory,
):
    """Check the validity of different correct phone numbers"""

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
@pytest.mark.parametrize(
    "phone",
    [
        ("+1234567890"),  # incorrect country code
        ("+7927"),  # too short
        ("+792712345678"),  # too long
        ("invalid"),  # is not a number
    ],
)
async def test_register_with_incorrect_phones(
    phone: str,
    auth_service: AuthService,
    register_request_schema_factory,
):
    """Check the validity of different incorrect phone numbers"""

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


@pytest.mark.asyncio
async def test_register_not_as_a_resident(
    auth_service: AuthService,
    register_request_schema_factory,
):
    """
    Проверка регистрации пользователя не как жилец.
    Ожидать PermisionDeniedError()
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
        role=UserRole.ADMIN,  # Try to register as an admin
        password="test_password",
    )

    # Get RegisterResponse
    with pytest.raises(AuthError):
        await auth_service.register(request=register_request)


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


@pytest.mark.asyncio
async def test_login_with_incorrect_data(
    auth_service: AuthService,
    register_request_schema_factory,
    login_request_schema_factory,
):
    """Verify that user can not login with incorrect data"""

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

    # Login user with incorrect data
    login_request = login_request_schema_factory(
        email="test@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424895",
        role=UserRole.RESIDENT,
        password="wrong_password",  # Wrong password
    )

    with pytest.raises(AuthError):
        await auth_service.login(login_request)


@pytest.mark.asyncio
async def test_login_tokens_updates(
    auth_service: AuthService,
    register_request_schema_factory,
    login_request_schema_factory,
):
    """
    Tokens are refreshed upon login—new tokens are generated each time you log in.
    Expect the refresh_token in the database to be updated with the new one.
    """
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
    login_response1 = await auth_service.login(login_request)
    await asyncio.sleep(0.65)  # Duration
    login_response2 = await auth_service.login(login_request)

    # Check that tokens in database is updated
    assert login_response1.access_token != login_response2.access_token
    assert login_response1.refresh_token != login_response2.refresh_token


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


@pytest.mark.asyncio
async def test_refresh_token_valid_refresh_token(
    auth_service: AuthService,
    register_request_schema_factory,
    token_refresh_request_schema_factory,
):
    """
    Обновление access токена по refresh токену - передать валидный refresh токен из БД
    ожидать новый access_token и время его жизни
    """
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

    # Use the refresh token from registration
    refresh_token = register_response.refresh_token
    assert refresh_token is not None

    # Create TokenRefreshRequest
    refresh_request = token_refresh_request_schema_factory(
        refresh_token=refresh_token,
    )

    await asyncio.sleep(0.65)  # Duration

    # Call refresh_token method
    refresh_response = await auth_service.refresh_token(refresh_request)

    # Assertions
    assert refresh_response.access_token is not None
    assert refresh_response.access_token != register_response.access_token
    assert refresh_response.access_token_expires_in > 0


@pytest.mark.asyncio
async def test_refresh_token_correct_type_in_payload(
    auth_service: AuthService,
    register_request_schema_factory,
    token_refresh_request_schema_factory,
):
    """
    Refresh токен имеет правильный тип - payload содержит "type": "refresh"
    ожидать успешную валидацию и выдачу нового токена
    """
    # Register user
    register_request = register_request_schema_factory(
        email="test2@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424896",
        role=UserRole.RESIDENT,
        password="test_password",
    )
    register_response = await auth_service.register(request=register_request)

    # Verify token type in payload
    payload = decode_token(register_response.refresh_token)
    assert payload is not None
    assert payload.get("type") == "refresh"

    # Create TokenRefreshRequest
    refresh_request = token_refresh_request_schema_factory(
        refresh_token=register_response.refresh_token,
    )

    # Call refresh_token method (should succeed)
    refresh_response = await auth_service.refresh_token(refresh_request)
    assert refresh_response.access_token is not None


@pytest.mark.asyncio
async def test_refresh_token_matches_stored_token(
    auth_service: AuthService,
    register_request_schema_factory,
    token_refresh_request_schema_factory,
    test_session: AsyncSession,
    user_service: UserService,
):
    """
    Проверка соответствия токена в БД - переданный токен совпадает с user.refresh_token
    ожидать успешное обновление
    """
    # Register user
    register_request = register_request_schema_factory(
        email="test3@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424897",
        role=UserRole.RESIDENT,
        password="test_password",
    )
    register_response = await auth_service.register(request=register_request)

    # Fetch user from DB and verify stored refresh token matches
    user = await user_service.repository.get_user(
        test_session, user_id=register_response.user.id
    )
    assert user.refresh_token == register_response.refresh_token

    # Create TokenRefreshRequest
    refresh_request = token_refresh_request_schema_factory(
        refresh_token=register_response.refresh_token,
    )

    # Call refresh_token method (should succeed)
    refresh_response = await auth_service.refresh_token(refresh_request)
    assert refresh_response.access_token is not None


@pytest.mark.asyncio
async def test_refresh_token_not_expired(
    auth_service: AuthService,
    register_request_schema_factory,
    token_refresh_request_schema_factory,
):
    """
    Проверка срока жизни refresh токена - token.expires_at еще не наступил
    ожидать успешную выдачу нового access токена
    """
    # Register user (token is fresh)
    register_request = register_request_schema_factory(
        email="test4@example.com",
        name="Foo",
        surname="Bar",
        patronymic="Barovich",
        address="Walt st.",
        apartment="12",
        phone="+79275424898",
        role=UserRole.RESIDENT,
        password="test_password",
    )
    register_response = await auth_service.register(request=register_request)

    # Create TokenRefreshRequest
    refresh_request = token_refresh_request_schema_factory(
        refresh_token=register_response.refresh_token,
    )

    # Call refresh_token method (should succeed because token not expired)
    refresh_response = await auth_service.refresh_token(refresh_request)
    assert refresh_response.access_token is not None
