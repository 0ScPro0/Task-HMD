from typing import Optional
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from sqladmin.authentication import AuthenticationBackend

from core.exceptions import AuthError


class AdminAuthBackend(AuthenticationBackend):
    """
    Authentication backend for SQLAdmin that checks session.
    Actual JWT authentication is done via FastAPI Depends in admin_router.
    """

    async def login(self, request: Request) -> bool:
        """
        Disable login form - admins must have token from main service
        """
        return False

    async def logout(self, request: Request) -> bool:
        """
        Logout - just clear session
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[Response]:
        """
        Check if admin was authenticated via Depends (session flag)
        """
        authenticated = request.session.get("authenticated", False)
        if not authenticated:
            raise AuthError("Authentication required")

        # All checks passed in Depends, just allow access
        return None
