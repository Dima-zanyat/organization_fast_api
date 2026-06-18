"""Тесты Repostory end-point."""

import pytest
from sqlalchemy import select


from app.repositories.department import DepartmentRepository
from app.repositories.employees import EmployeesRepository
from app.schemas.department import SDepartmentCreate
from app.schemas.empoyees import SEmployeesCreate
from app.models.department import DepartmentModel
from tests.constant import (
    BASE_DEPARTMENT_NAME,
    CREATE_DEPARTMENT_URL,
    CREATE_EMPLOYEES_URL,
    GET_DEPARTMENTS_TREE_URL,
    PATCH_DEPARTMENT,
    TEST_DEPTH,
    NAME_EMPLOYE,
    POSITION_EMPLOYE,
    NAME_EMPLOYE,
    POSITION_EMPLOYE,
    MODE_DELETE_CASCADE,
    MODE_DELETE_REASSIGN,
)
from tests.utils import check_dep_created, check_employe_create


@pytest.mark.asyncio
async def test_create_dep_repository(test_session):
    data = SDepartmentCreate(
        name=BASE_DEPARTMENT_NAME,
        parent_id=None,
    )
    department = await DepartmentRepository.create(
        data=data,
        session=test_session,
    )

    await check_dep_created(test_session, department)


@pytest.mark.asyncio
async def test_create_employee(test_session):
    result = await test_session.scalars(select(DepartmentModel))
    department = result.first()
    data = SEmployeesCreate(full_name=NAME_EMPLOYE, position=POSITION_EMPLOYE)
    employee = await EmployeesRepository.create(
        department.id,
        data=data,
        session=test_session,
    )
    await check_employe_create(test_session, employee)
