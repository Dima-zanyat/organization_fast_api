"""Тесты API end-point."""

import pytest
from http import HTTPStatus

from tests.constant import (
    BASE_DEPARTMENT,
    CREATE_DEPARTMENT_URL,
    CREATE_EMPLOYEES_URL,
    GET_DEPARTMENTS_TREE_URL,
    TEST_DEPTH,
    NAME_EMPLOYE,
    POSITION_EMPLOYE,
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
        params={"depth": TEST_DEPTH},
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_post_employees(client):
    response = await client.post(
        CREATE_EMPLOYEES_URL,
        json={
            "full_name": NAME_EMPLOYE,
            "position": POSITION_EMPLOYE,
        },
    )
    print("TEST_EMPLOYEES", response)

    assert response.status_code == HTTPStatus.CREATED
