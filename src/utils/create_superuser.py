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


async def create_superuser(
    name: str = "Danya",
    surname: str = "Zolik",
    position_id: int = None,
    email: EmailStr = "root@example.com",
    password: str = SUPER_USER_PASSWORD,
    is_active: bool = True,
    is_superuser: bool = True,
    is_verified: bool = True,
    birthday: date = date.today(),
):
    user_create = UserCreate(
        name=name,
        surname=surname,
        position_id=position_id,
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
                        await create_user(
                            user_manager=user_manager, user_create=user_create
                        )
    except UserAlreadyExists:
        ...
