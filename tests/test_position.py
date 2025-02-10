from fastapi import status
import pytest

base = "/position/"


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_201_CREATED),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_position_add(client_fixture, expected_status):
    respond = await client_fixture.post(
        base + "add",
        json={"section_id": 1, "name": "Position"},
    )
    assert respond.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("regular_client", status.HTTP_200_OK),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_get_position(client_fixture, expected_status):
    respond = await client_fixture.get(base + "Position")
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
async def test_patch_position(client_fixture, expected_status):
    respond = await client_fixture.patch(base + "update/Position/1")
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
        {"filter_name": "Менеджер"},
        {"page_size": 1},
        {"page_size": 100},
        {"last_position_name": "Разработчик"},
        {"section": 1},
        {"desc": True, "page_size": 50, "filter_name": "Аналитик"},
        {"desc": False, "section": 2, "last_position_name": "Тестировщик"},
    ],
)
async def test_get_positions(client_fixture, expected_status, params):
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
async def test_delete_position(client_fixture, expected_status):
    respond = await client_fixture.delete(base + "delete/Position")
    assert respond.status_code == expected_status
    if respond.status_code == status.HTTP_200_OK:
        respond = await client_fixture.get(base + "Position")
        assert respond.status_code == status.HTTP_404_NOT_FOUND
