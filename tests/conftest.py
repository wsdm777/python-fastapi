import asyncio
from contextlib import asynccontextmanager
from datetime import date
import logging
from typing import AsyncGenerator
from argon2 import hash_password
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.databasemodels import Base, Position, Section, User
from src.database import get_async_session
from src.main import app
from src.config import SUPER_USER_PASSWORD
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from src.user.schemas import UserCreate, UserRead

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


async def setub_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with test_async_session_maker() as session:
        admin = User(
            name="Test",
            surname="Test",
            email="root@example.com",
            hashed_password=pass_hash,
            is_superuser=True,
            is_verified=True,
            birthday=date.today(),
        )

        regular_user = User(
            name="Regular",
            surname="User",
            email="test@example.com",
            hashed_password=pass_hash,
            is_superuser=False,
            is_verified=False,
            birthday=date.today(),
        )

        section = Section(name="Отдел", head_id=1)

        position = Position(section_id=1, name="Должность")

        session.add_all([admin, regular_user, section, position])
        await session.commit()


def pytest_sessionstart(session):
    asyncio.run(setub_db())


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session_maker() as session:
        async with session.begin():
            yield session


@pytest.fixture(autouse=True)
async def override_db_dependency():
    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_async_session_maker() as session:
            yield session

    app.dependency_overrides[get_async_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def admin_auth_cookies():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/auth/login",
            data={
                "grant_type": "password",
                "username": "root@example.com",
                "password": SUPER_USER_PASSWORD,
                "scope": "",
                "client_id": "string",
                "client_secret": "string",
            },
        )
        if response.status_code != status.HTTP_204_NO_CONTENT:
            pytest.fail("Не удалось авторизовать администратора")
    return response.cookies


@pytest.fixture(scope="function")
async def admin_client(admin_auth_cookies):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        cookies=admin_auth_cookies,
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def regular_auth_cookies():

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/auth/login",
            data={
                "grant_type": "password",
                "username": "test@example.com",
                "password": SUPER_USER_PASSWORD,
                "scope": "",
                "client_id": "string",
                "client_secret": "string",
            },
        )
        if response.status_code != status.HTTP_204_NO_CONTENT:
            pytest.fail("Не удалось авторизовать пользователя")
    return response.cookies


@pytest.fixture(scope="function")
async def regular_client(regular_auth_cookies):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
        cookies=regular_auth_cookies,
    ) as client:
        yield client


@pytest.fixture(scope="function")
async def unauthorized_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c


@pytest.fixture
def client_fixture(request):
    return request.getfixturevalue(request.param)
