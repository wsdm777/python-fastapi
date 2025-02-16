from fastapi import status
import pytest

base = "/vacation/"


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_201_CREATED),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_vacation_create(client_fixture, expected_status):
    respond = await client_fixture.post(
        base + "create",
        json={
            "receiver_id": 2,
            "start_date": "2024-02-10",
            "end_date": "2026-02-10",
            "description": "test",
        },
    )
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_200_OK),
        ("regular_client", status.HTTP_200_OK),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_get_vacation(client_fixture, expected_status):
    respond = await client_fixture.get(base + "1")
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_200_OK),
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
        {"status": "active"},
        {"status": "future"},
        {"status": "past"},
        {"page_size": 1},
        {"page_size": 100},
        {"last_vacation_id": 123},
        {"receiver_id": 1},
        {"giver_id": 2},
        {"desc": True, "page_size": 100, "status": "active"},
        {"desc": False, "status": "future", "receiver_id": 3},
        {"page_size": 50, "status": "past", "giver_id": 4},
    ],
)
async def test_get_vacations(client_fixture, expected_status, params):
    respond = await client_fixture.get(base + "list/", params=params)
    assert respond.status_code == expected_status
