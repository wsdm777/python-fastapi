import contextlib
from datetime import date
from pydantic import EmailStr
from sqlalchemy import insert, select

from src.auth.router import hash_password
from src.databasemodels import User
from src.config import SUPER_USER_EMAIL, SUPER_USER_PASSWORD
from src.database import get_async_session
from src.utils.logger import logger

get_async_session_context = contextlib.asynccontextmanager(get_async_session)


async def create_superuser(
    name: str = "Danya",
    surname: str = "Zolik",
    email: EmailStr = SUPER_USER_EMAIL,
    password: str = SUPER_USER_PASSWORD,
    is_superuser: bool = True,
    birthday: date = date.today(),
):
    hashed_password = hash_password(password=password)
    user_create = {
        "name": name,
        "surname": surname,
        "position_id": None,
        "email": email,
        "hashed_password": hashed_password,
        "is_superuser": is_superuser,
        "birthday": birthday,
    }
    async with get_async_session_context() as session:
        query = select(User.id).filter(User.is_superuser == True).limit(1)
        result = await session.execute(query)
        if result.scalar() is None:
            stmt = insert(User).values(user_create)
            await session.execute(stmt)
            await session.commit()
            logger.info("Root created")
