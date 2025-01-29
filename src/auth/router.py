from fastapi import APIRouter, Depends
from src.auth.authentification import fastapi_users
from src.user.schemas import UserCreate, UserRead
from src.user.router import get_current_superuser
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from src.auth.authentification import fastapi_users, auth_backend

router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    dependencies=[Depends(get_current_superuser)],
)

auth_router = fastapi_users.get_auth_router(auth_backend)

auth_router.routes = [auth_router.routes[0]]  # Только login route

router.include_router(auth_router)


@router.post("/logout")
async def custom_logout(response: Response, request: Request):
    cookies = request.cookies

    if "authcook" not in cookies:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    expired_date = datetime.now(timezone.utc) - timedelta(days=1)

    response.set_cookie(
        "authcook",
        value="",
        expires=expired_date,
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return {"message": "Successfully logged out"}
