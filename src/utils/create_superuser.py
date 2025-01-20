import contextlib
from datetime import date
from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr
from sqlalchemy import select

from src.databasemodels import User
from src.config import SUPER_USER_PASSWORD
from src.auth.manager import UserManager, get_user_manager
from src.database import get_async_session, get_user_db
from src.user.schemas import UserCreate

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(user_manager: UserManager, user_create: UserCreate):
    user = await user_manager.create(user_create=user_create, safe=False)
    return user


default_name = "Danya"
default_surname = "Zolik"
default_position_name = None
default_email = "root@example.com"
default_password = SUPER_USER_PASSWORD
default_is_active = True
default_is_superuser = True
default_is_verified = True
default_birthday = date.today()


async def create_superuser(
    name: str = default_name,
    surname: str = default_surname,
    position_name: int = default_position_name,
    email: EmailStr = default_email,
    password: str = default_password,
    is_active: bool = default_is_active,
    is_superuser: bool = default_is_superuser,
    is_verified: bool = default_is_verified,
    birthday: date = default_birthday,
):
    user_create = UserCreate(
        name=name,
        surname=surname,
        position_name=position_name,
        email=email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
        birthday=birthday,
    )
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    query = select(User.id).filter(User.is_superuser == True).limit(1)
                    result = await session.execute(query)
                    if result.scalar() is None:
                        user = await create_user(
                            user_manager=user_manager, user_create=user_create
                        )
                        return user
    except UserAlreadyExists:
        ...
