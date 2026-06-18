from sqlalchemy import select

from app.models.department import DepartmentModel
from app.models.employees import EmployeeModel


async def check_dep_created(test_session, expected_dep):

    result = await test_session.scalars(select(DepartmentModel))
    actual_dep = result.first()
    assert actual_dep.id == expected_dep.id
    assert actual_dep.name == expected_dep.name


async def check_employe_create(test_session, employee):
    result = await test_session.scalars(select(EmployeeModel))
    actual_employe = result.first()
    assert employee.id == actual_employe.id
    assert employee.department_id == actual_employe.department_id
    assert employee.full_name == actual_employe.full_name
