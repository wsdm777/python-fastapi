import asyncio
from datetime import date
import logging
from typing import AsyncGenerator
import fakeredis
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status
from redis.asyncio import Redis
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.auth.router import hash_password
from src.databasemodels import Base, Position, Section, User
from src.database import get_async_session
from src.main import app
from src.config import (
    DB_NAME,
    DB_PASS,
    DB_PORT,
    DB_USER,
    REDIS_PORT,
    SUPERUSER_PASSWORD,
)
import src.services.redis as auth_service

logging.basicConfig(level=logging.DEBUG)
DB_HOST = "localhost"
REDIS_HOST = "localhost"

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
        hashed_password = hash_password(password=SUPERUSER_PASSWORD)
        admin = User(
            name="Test",
            surname="Test",
            email="root@example.com",
            hashed_password=hashed_password,
            is_superuser=True,
            birthday=date.today(),
        )

        regular_user = User(
            name="Regular",
            surname="User",
            email="test@example.com",
            hashed_password=hashed_password,
            is_superuser=False,
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


@pytest.fixture(scope="function", autouse=True)
async def mock_redis(monkeypatch):
    client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    monkeypatch.setattr(auth_service, "redis_client", client)
    yield client
    await client.aclose()


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
            json={
                "email": "root@example.com",
                "password": SUPERUSER_PASSWORD,
            },
        )
        if response.status_code != status.HTTP_200_OK:
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
            json={
                "email": "test@example.com",
                "password": SUPERUSER_PASSWORD,
            },
        )
        if response.status_code != status.HTTP_200_OK:
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
