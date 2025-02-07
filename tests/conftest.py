from datetime import date
import logging
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.databasemodels import Base, User
from src.database import get_async_session
from src.main import app
from src.config import SUPER_USER_PASSWORD
from src.utils.create_superuser import create_superuser
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

logging.basicConfig(level=logging.DEBUG)

pass_hash = "$argon2id$v=19$m=65536,t=3,p=4$1GTdgCCgFwuhT0irVuKZEQ$B6tV6CJMAr4py31Q4ALNHbuBJcR2iIJCdHY9jBhanCQ"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={"server_settings": {"search_path": "test"}},
)
test_async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
async def override_db_dependency(setup_test_db):
    async def _override() -> AsyncGenerator[AsyncSession, None]:
        async with test_async_session_maker() as session:
            yield session

    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.clear()


async def create_superuser(session):
    stmt = insert(User).values(
        {
            "name": "Danya",
            "surname": "Zolik",
            "position_id": None,
            "email": "root@example.com",
            "hashed_password": pass_hash,
            "is_active": True,
            "is_superuser": True,
            "is_verified": True,
            "birthday": date.today(),
        }
    )
    await session.execute(stmt)
    await session.commit()


@pytest.fixture(scope="session")
async def client(override_db_dependency):

    async with test_async_session_maker() as session:
        await create_superuser(session=session)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:

        response = await c.post(
            "/auth/login",
            data={
                "grant_type": "password",
                "username": "root@example.com",
                "password": SUPER_USER_PASSWORD,
                "scope": "",
                "client_id": "string",
                "client_secret": "string",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != status.HTTP_204_NO_CONTENT:
            pytest.exit(f"Основной тест не прошел, завершение сессии {response.text}")

        yield c
