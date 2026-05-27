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
    ) -> Optional[SDepartmentTree]:
        """Получение детальной информации о древе департамента."""
        if data.depth <= 0:
            return None
        department = cls.validate_department(
            await DepartmentRepository.get_by_id(department_id=department_id)
        )

        employees: list[SEmployees] = []
        if data.include_employees:
            employees = await cls.get_emlpoyees(department_id=department_id)
        children: list[SDepartmentTree] = []
        new_data = SDepartmentGet(
            depth=data.depth - 1,
            include_employees=data.include_employees,
        )
        for child in department.sub_departments:
            child_tree = await cls.get_detail_employee_tree(
                department_id=child.id,
                data=new_data,
            )
            if child_tree:
                children.append(child_tree)
        response = SDepartmentTree.model_validate(department)
        response.employees = employees
        response.children = children
        return response
