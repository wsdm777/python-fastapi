from fastapi import HTTPException, Response, status
from fastapi_users.jwt import generate_jwt
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from src.auth.manager import get_user_manager
from src.databasemodels import User
from src.config import SECRET
from src.auth.JWT import CustomJWTStrategy


class CustomAuthenticationBackend(AuthenticationBackend):
    async def logout(response: Response):
        if not response.cookies.get("authcook"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unauthorized"
            )

        response.delete_cookie("authcook")
        return {"msg": "Successfully logged out"}


cookie_transport = CookieTransport(cookie_name="authcook")


def get_jwt_strategy() -> CustomJWTStrategy:
    return CustomJWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = CustomAuthenticationBackend(
    name="jwt", transport=cookie_transport, get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
