from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.databasemodels import User
from src.database import get_user_db
from src.utils.logger import logger


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def on_after_register(
        self, user: User, request: Optional[Request] = None
    ) -> None:
        logger.info(f"User {user.id} registered")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
