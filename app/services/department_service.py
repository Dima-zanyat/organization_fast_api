"""Файл сервисов и бизнес-логики приложения."""

import logging

from models.department import DepartmentModel
from repositories.department import DepartmentRepository
from schemas.department import SDepartmentCreate


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
    async def get_detail_employee_tree(
        cls,
        department_id: int,
        depth: int,
        include_employees: bool,
    ):