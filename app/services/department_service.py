"""Файл сервисов и бизнес-логики приложения."""

from typing import Optional

from models.department import DepartmentModel
from models.employees import EmployeeModel
from repositories.department import DepartmentRepository
from repositories.employees import EmployeesRepository
from schemas.department import (
    SDepartmentCreate,
    SDepartmentGet,
    SDepartmentTree,
)
from schemas.empoyees import SEmployees


class DepartmentService:
    """Операции с департамент-сервисом."""

    @classmethod
    async def create_department(
        cls,
        data: SDepartmentCreate,
    ) -> DepartmentModel:
        """Логика создания департамента."""
        if data.parent_id is not None:
            parent = await DepartmentRepository.get_by_id(department_id=data.parent_id)
            if parent is None:
                raise ValueError("Указанный департамент не найден.")

        return await DepartmentRepository.create(data)

    @classmethod
    def validate_department(
        cls,
        department: Optional[DepartmentModel],
    ) -> DepartmentModel:
        """Проверка на exist по department_id."""
        if department is None:
            raise ValueError("Объект не найден.")
        return department

    @classmethod
    async def get_emlpoyees(cls, department_id: int) -> list[SEmployees]:
        """Получение списка сотрудников."""
        employees_orm: list[EmployeeModel] = (
            await EmployeesRepository.list_by_department_id(department_id=department_id)
        )
        employees = [SEmployees.model_validate(employee) for employee in employees_orm]
        return employees

    @classmethod
    async def get_detail_employee_tree(
        cls,
        department_id: int,
        data: SDepartmentGet,
    ):
        """Получение детальной информации о древе департамента."""
        if data.depth <= 0:
            return None
        departments = await DepartmentRepository.get_subtree(
            department_id=department_id,
            depth=data.depth,
        )
        departmnets_ids = [department.id for department in departments]
        employee_by_departmnets_ids: dict[int, list[SEmployees]] = {
            dep_id: [] for dep_id in departmnets_ids
        }
        if data.include_employees:
            employee_orm = await EmployeesRepository.list_by_departments_ids(
                department_ids=departmnets_ids,
            )
            for employee in employee_orm:
                employee_by_departmnets_ids.setdefault(
                    employee.department_id, []
                ).append(SEmployees.model_validate(employee))
        departments_by_id = {dep.id: dep for dep in departments}
        child_by_department: dict[int | None, list[DepartmentModel]] = {}
        for department in departments:
            child_by_department.setdefault(department.parent_id, []).append(department)

        def tree_department(department: DepartmentModel):
            node = SDepartmentTree.model_validate(department)
            node.employees = employee_by_departmnets_ids.get(department.id, [])
            node.children = [
                tree_department(child)
                for child in child_by_department.get(department.id, [])
            ]
            return node

        root_dep = departments_by_id[department_id]
        return tree_department(root_dep)
