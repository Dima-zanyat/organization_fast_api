"""Тесты API end-point."""

import pytest
from http import HTTPStatus

from tests.constant import (
    BASE_DEPARTMENT_NAME,
    CREATE_DEPARTMENT_URL,
    CREATE_EMPLOYEES_URL,
    GET_DEPARTMENTS_TREE_URL,
    TEST_DEPTH,
    NAME_EMPLOYE,
    POSITION_EMPLOYE,
    MODE_DELETE_CASCADE,
    MODE_DELETE_REASSIGN,
)


@pytest.mark.asyncio
async def test_create_base_department(client):
    """Тест на создании сотрудника."""
    response = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": BASE_DEPARTMENT_NAME,
            "parent_id": None,
        },
    )
    result = response.json()
    print("TEST", result)
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_create_subdepartment(client, base_department):
    response = await client.post(
        CREATE_DEPARTMENT_URL,
        json={
            "name": BASE_DEPARTMENT_NAME,
            "parent_id": base_department.get("id", None),
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
    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_patch_department(
    client,
    department_tree,
    get_patch_url,
):
    response = await client.patch(
        get_patch_url, json={"parent_id": department_tree.get("dep_b").get("id")}
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_department_cascade(
    client,
    department_tree,
    delete_dep_url_cascade,
):
    response = await client.delete(
        delete_dep_url_cascade,
        params={
            "mode": MODE_DELETE_CASCADE,
        },
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_department_reassign(
    client,
    department_tree,
    delete_dep_url_cascade,
):
    response = await client.delete(
        delete_dep_url_cascade,
        params={
            "mode": MODE_DELETE_REASSIGN,
            "reassign_to_department_id": department_tree.get("dep_a").get("id"),
        },
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
