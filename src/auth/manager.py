from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from src.user.models import User
from src.database import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]): ...


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
