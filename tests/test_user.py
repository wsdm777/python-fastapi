from fastapi import status
import pytest

from src.config import SUPERUSER_PASSWORD

base = "/user/"


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("regular_client", status.HTTP_200_OK),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
@pytest.mark.asyncio
async def test_get_user(client_fixture, expected_status):
    respond = await client_fixture.get(base + "root@example.com")
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_201_CREATED),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
@pytest.mark.asyncio
async def test_register(client_fixture, expected_status):
    respond = await client_fixture.post(
        "auth/register",
        json={
            "email": "123@example.com",
            "password": "test",
            "is_superuser": True,
            "name": "test",
            "surname": "test",
            "birthday": "2000-02-08",
        },
    )
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_200_OK),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_update(client_fixture, expected_status):
    respond = await client_fixture.patch(base + "grand-admin/123@example.com")
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("regular_client", status.HTTP_200_OK),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
@pytest.mark.parametrize(
    "params",
    [
        {},
        {"desc": True},
        {"desc": False},
        {"filter_surname": "Иванов"},
        {"page_size": 1},
        {"page_size": 100},
        {"last_name": "Петров"},
        {"last_surname": "Сидоров"},
        {"on_vacation_only": True},
        {"on_vacation_only": False},
        {"desc": True, "page_size": 100, "on_vacation_only": True},
        {"desc": False, "filter_surname": "Смирнов", "last_name": "Павлов"},
        {"page_size": 10, "last_name": "Козлов", "last_surname": "Орлов"},
    ],
)
async def test_get_users(client_fixture, expected_status, params):
    respond = await client_fixture.get(base + "list/", params=params)
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_200_OK),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_user_position_patch(client_fixture, expected_status):
    respond = await client_fixture.patch(base + "123@example.com/position/1")
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_200_OK),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_delete(client_fixture, expected_status):
    respond = await client_fixture.delete(base + "123@example.com")
    assert respond.status_code == expected_status
    if respond.status_code == status.HTTP_200_OK:
        respond = await client_fixture.get(base + "123@example.com")
        assert respond.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("regular_client", status.HTTP_200_OK),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_password_change(client_fixture, expected_status, mock_redis):
    respond = await client_fixture.patch(
        base + "change-password", json={"new_password": SUPERUSER_PASSWORD}
    )
    assert respond.status_code == expected_status
    if respond.status_code == 200:
        key = "user_sessions:2"
        assert await mock_redis.exists(key) == 0
