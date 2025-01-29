from typing import Annotated, Optional
from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.auth.JWT import get_current_superuser
from src.auth.schemas import UserTokenInfo
from src.databasemodels import User
from src.database import get_user_db
from src.utils.logger import logger


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ) -> None:
        if user.email == "root@example.com":
            logger.info("Root user created")
        else:
            creator = get_current_superuser(request=request)
            logger.info(f"{creator.email}: User {user.email} registered")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        logger.info(f"User {user.email} login")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
