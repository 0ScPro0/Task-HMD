from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exceptions import AuthError, InvalidTokenTypeError
from core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    decode_token,
)

from database import User
from repositories import UserRepository

from schemas.auth import (
    LoginRequest,
    RegisterRequest,
    LoginResponse,
    RegisterResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from schemas.user import UserResponse, UserCreate

from utils.logger import log
from utils.serializator import resolve_phone


class AuthService:
    """Service for authentication and authorization"""

    def __init__(self, session: AsyncSession, user_repository: UserRepository):
        self.session = session
        self.user_repository = user_repository

    @log
    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """
        Register a new user

        Args:
            user (RegisterRequest): User data

        Raises:
            AuthError: If user with the same email already exists

        Returns:
            User: Created user
        """
        # Resolve phone
        phone = await resolve_phone(request.phone)
        if not phone:
            raise AuthError(f"Incorrect phone number: {request.phone}")

        # Check if user with the same phone or email already exists
        if await self.user_repository.get_user_by_phone_or_email(
            self.session, phone=phone, email=request.email
        ):
            raise AuthError("User with this phone or email already exists")

        # Hash password
        password_hash = hash_password(request.password)

        # Create UserCreate object
        user_create = UserCreate(
            email=request.email,
            name=request.name,
            surname=request.surname,
            patronymic=request.patronymic,
            address=request.address,
            apartment=request.apartment,
            phone=phone,
            role=request.role,
            password_hash=password_hash,
        )

        # Create user in database
        user = await self.user_repository.create_user(
            session=self.session, user_object=user_create
        )

        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # Calculate expiration times
        access_token_expires_in = settings.security.access_token_expire_minutes
        refresh_token_expires_in = settings.security.refresh_token_expire_days

        # Store refresh token in database
        await self._store_refresh_token(user_id=user.id, refresh_token=refresh_token)

        # Return response
        return RegisterResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=access_token_expires_in,
            refresh_token_expires_in=refresh_token_expires_in,
        )

    @log
    async def login(self, request: LoginRequest) -> LoginResponse:
        """
        Login a user

        Args:
            user (LoginRequest): User credentials

        Raises:
            AuthError: If credentials are invalid

        Returns:
            dict: User data and tokens
        """
        # Resolve phone
        phone = await resolve_phone(request.phone)
        if not phone:
            raise AuthError(f"Incorrect phone number: {request.phone}")

        # Get user by phone or email
        user = await self.user_repository.get_user_by_phone_or_email(
            self.session, phone=request.phone, email=request.email
        )
        if not user:
            raise AuthError("Invalid credentials")

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise AuthError("Invalid credentials")

        # Check if user is active
        if not await self.user_repository.is_active(self.session, user_id=user.id):
            raise AuthError("User is deactivated")

        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        # Calculate expiration times
        access_token_expires_in = settings.security.access_token_expire_minutes * 60
        refresh_token_expires_in = (
            settings.security.refresh_token_expire_days * 24 * 60 * 60
        )

        # Store refresh token in database
        await self._store_refresh_token(user_id=user.id, refresh_token=refresh_token)

        # Return response
        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=access_token_expires_in,
            refresh_token_expires_in=refresh_token_expires_in,
        )

    @log
    async def logout(self, user_id: int):
        """
        Logout user by clearing refresh token

        Args:
            user_id (int): User ID

        Returns:
            True if successful
        """
        # Clear refresh token in database
        await self.user_repository.clear_refresh_token(
            session=self.session, user_id=user_id
        )

        return True

    @log
    async def get_current_user(self, token: str):
        """
        Get current user from token

        Args:
            token (str): Access token

        Raises:
            AuthError: If token is invalid or expired

        Returns:
            User: Current user
        """
        # Decode token
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise AuthError("Invalid token")

        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Invalid token")

    @log
    async def refresh_token(
        self, refresh_request: TokenRefreshRequest
    ) -> TokenRefreshResponse:
        """
        Refresh access token using refresh token

        Args:
            refresh_request (TokenRefreshRequest): Refresh token

        Raises:
            AuthError: If refresh token is invalid or expired

        Returns:
            TokenRefreshResponse: New access token
        """
        # Decode refresh token
        payload = decode_token(refresh_request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthError("Invalid refresh token")

        # Check if token is expired
        exp = payload.get("exp")
        if not exp or datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
            timezone.utc
        ):
            raise AuthError("Refresh token expired")

        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise AuthError("Invalid refresh token")

        # Get user from database
        user = await self.user_repository.get(self.session, user_id)
        if not user:
            raise AuthError("User not found")

        # Check if user is active
        if not await self.user_repository.is_active(self.session, user_id=user.id):
            raise AuthError("User is deactivated")

        # Verify refresh token matches stored token
        if user.refresh_token != refresh_request.refresh_token:
            raise AuthError("Invalid refresh token")

        # Check if stored refresh token is expired
        if user.refresh_token_expires_at:
            # Convert to aware datetime if necessary
            expires_at = user.refresh_token_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < datetime.now(timezone.utc):
                raise AuthError("Refresh token expired")

        # Create new access token
        new_access_token = create_access_token({"sub": str(user.id)})
        access_token_expires_in = settings.security.access_token_expire_minutes * 60

        # Return response
        return TokenRefreshResponse(
            access_token=new_access_token,
            access_token_expires_in=access_token_expires_in,
        )

    @log
    async def _store_refresh_token(self, user_id, refresh_token: str) -> bool:
        """
        Store refresh token in database

        Args:
            refresh_token (str): Refresh token

        Raises:
            InvalidTokenTypeError if can not store refresh token

        Returns:
            True if successful
        """
        try:
            refresh_token_payload = decode_token(refresh_token)
            if refresh_token_payload:
                refresh_token_expires_at = datetime.fromtimestamp(
                    refresh_token_payload["exp"], tz=timezone.utc
                )
                await self.user_repository.update_refresh_token(
                    session=self.session,
                    user_id=user_id,
                    refresh_token=refresh_token,
                    expires_at=refresh_token_expires_at,
                )
            return True
        except Exception as e:
            raise InvalidTokenTypeError(f"Can not store refresh token: {e}")
