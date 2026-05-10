from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/admins", tags=["admins"])


@router.get("/{token}")
async def get_admin_page(token: str):
    response = RedirectResponse(url="/admin", status_code=302)
    # Set cookie to authorization
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response
