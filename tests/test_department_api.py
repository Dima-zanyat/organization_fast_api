"""Тесты API end-point."""

import pytest
from http import HTTPStatus

from tests.constant import BASE_DEPARTMENT, CREATE_DEPARTMENT_URL


@pytest.mark.asyncio
async def test_create_department(client):
    response = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": BASE_DEPARTMENT,
            "parent_id": None,
        },
    )
    assert response.status_code == HTTPStatus.CREATED
