from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from src.auth.models import User


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_id(userid: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(User).where(User.id == userid)
    result = await session.execute(stmt)
    user = result.scalars().one()
    return user