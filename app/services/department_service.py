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
    SDepartmentUpdate,
    SDepartmentResponse,
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
    ) -> SDepartmentTree:
        """Получение дерева департаментов."""
        departments = await DepartmentRepository.get_subtree_by_depth(
            department_id=department_id,
            depth=data.depth,
        )

        departments_ids: list[int] = [department.id for department in departments]
        departments_by_id: dict[int, DepartmentModel] = {
            dep.id: dep for dep in departments
        }

        employees_by_department: dict[int, list[SEmployees]] = {
            dep_id: [] for dep_id in departments_ids
        }

        if data.include_employees:
            employees = await EmployeesRepository.list_by_departments_ids(
                department_ids=departments_ids
            )
            for employee in employees:
                employees_by_department.setdefault(employee.department_id, []).append(
                    SEmployees.model_validate(employee)
                )
        child_by_departments: dict[int | None, list[DepartmentModel]] = {}

        for department in departments:
            child_by_departments.setdefault(department.parent_id, []).append(department)

        def get_tree(department: DepartmentModel) -> SDepartmentTree:
            """Рекурсивное получение дерева."""
            node = SDepartmentTree.model_validate(department)
            node.employees = employees_by_department.get(department.id, [])
            node.children = [
                get_tree(child) for child in child_by_departments.get(department.id, [])
            ]
            return node

        root = departments_by_id.get(department_id)
        if root is None:
            raise ValueError("Департамент не найден")
        return get_tree(department=root)

    @classmethod
    async def update_department(
        cls,
        department_id: int,
        data: SDepartmentUpdate,
    ) -> SDepartmentResponse:
        department = cls.validate_department(
            await DepartmentRepository.get_by_id(department_id)
        )

        if data.parent_id is not None:
            new_parent = cls.validate_department(
                await DepartmentRepository.get_by_id(data.parent_id)
            )

            if department.id == new_parent.id:
                raise ValueError("Нельзя сделать родителем самого себя.")

            subtree = await DepartmentRepository.get_full_subtree(department.id)

            subtree_ids = {dep.id for dep in subtree}

            if new_parent.id in subtree_ids:
                raise ValueError(
                    "Нельзя переместить департамент внутрь своего поддерева."
                )

        updated_department = await DepartmentRepository.update(
            department_id=department.id,
            parent_id=new_parent.id,
        )
        return SDepartmentResponse.model_validate(updated_department)
