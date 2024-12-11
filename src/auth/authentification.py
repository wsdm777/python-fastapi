from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    CookieTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from src.auth.manager import get_user_manager
from src.databasemodels import User
from src.config import SECRET


cookie_transport = CookieTransport(cookie_name="authcook")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=36000)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
