"""Тесты API end-point."""

import pytest
from http import HTTPStatus

from tests.constant import (
    BASE_DEPARTMENT,
    CREATE_DEPARTMENT_URL,
    GET_DEPARTMENTS_TREE_URL,
)


@pytest.mark.asyncio
async def test_create_department(client):
    """Тест на создании сотрудника."""
    response = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": BASE_DEPARTMENT,
            "parent_id": None,
        },
    )
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_get_department(client):
    response = await client.get(
        GET_DEPARTMENTS_TREE_URL,
        params={"depth": 1},
    )

    assert response.status_code == HTTPStatus.OK
