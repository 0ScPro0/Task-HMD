# admin/auth.py
from typing import Optional
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from sqladmin.authentication import AuthenticationBackend
import jwt
from core.config import settings
from core.security import decode_token
from core.exceptions import AuthError


class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # Get token
        token_cookie = request.cookies.get("access_token")

        if not token_cookie:
            return False

        token = token_cookie.replace("Bearer ", "")

        try:
            # Verify JWT
            payload = decode_token(token)

            if payload.get("role") != "admin":
                return False

            # Save data to session
            request.session["authenticated"] = True
            request.session["user_id"] = payload.get("sub")
            request.session["role"] = payload.get("role")

            return True

        except jwt.InvalidTokenError:
            return False
        except Exception:
            return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Check session
        if request.session.get("authenticated"):
            return True

        return False
