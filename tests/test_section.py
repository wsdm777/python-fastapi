from fastapi import status
import pytest

base = "/section/"


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("admin_client", status.HTTP_201_CREATED),
        ("regular_client", status.HTTP_403_FORBIDDEN),
        ("unauthorized_client", status.HTTP_401_UNAUTHORIZED),
    ],
    indirect=["client_fixture"],
)
async def test_section_create(client_fixture, expected_status):
    respond = await client_fixture.post(
        base + "create",
        json={"name": "Section"},
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
async def test_get_section(client_fixture, expected_status):
    respond = await client_fixture.get(base + "Section")
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
async def test_put_section(client_fixture, expected_status):
    respond = await client_fixture.put(
        base + "Section/1",
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
@pytest.mark.parametrize(
    "params",
    [
        {},
        {"desc": True},
        {"desc": False},
        {"filter_name": "Отдел разработки"},
        {"page_size": 1},
        {"page_size": 100},
        {"last_section_name": "Отдел тестирования"},
        {"desc": True, "page_size": 50, "filter_name": "Отдел аналитики"},
        {"desc": False, "page_size": 10, "last_section_name": "Отдел маркетинга"},
    ],
)
async def test_get_sections(client_fixture, expected_status, params):
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
async def test_delete_section(client_fixture, expected_status):
    respond = await client_fixture.delete(base + "Section/remove")
    assert respond.status_code == expected_status
    if respond.status_code == status.HTTP_200_OK:
        respond = await client_fixture.get(base + "Section")
        assert respond.status_code == status.HTTP_404_NOT_FOUND
