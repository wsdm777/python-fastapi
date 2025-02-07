from fastapi import status
import pytest

base = "/user/"
json_header = {"accept": "application/json"}


@pytest.mark.asyncio
async def test_request(client):
    respond = await client.get(base + "root@example.com", headers=json_header)
    assert respond.status_code == status.HTTP_200_OK
