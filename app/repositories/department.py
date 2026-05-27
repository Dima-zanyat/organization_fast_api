"""Файл для репозитория подразделений."""

from typing import Optional

from sqlalchemy import select

from database import new_session
from schemas.department import SDepartmentCreate, SDepartmentResponse
from models.department import DepartmentModel


class DepartmentRepository:
    """Репозиторий для CRUD операций."""

    @classmethod
    async def create(
        cls,
        data: SDepartmentCreate,
    ) -> DepartmentModel:
        """Создание департамента."""
        async with new_session() as session:
            department_data = data.model_dump()
            department = DepartmentModel(**department_data)
            session.add(department)
            await session.commit()
            await session.refresh(department)
            return department

    @classmethod
    async def get_by_id(
        cls,
        department_id: int,
    ) -> Optional[DepartmentModel]:
        """Получение объекта департамента."""
        async with new_session() as session:
            department = await session.get(
                DepartmentModel,
                department_id,
            )
            return department

    @classmethod
    async def get_subtree(
        cls,
        department_id: int,
        depth:int,
    ):



    @classmethod
    async def list_by_parent_id(
        cls,
        parent_id: int,
    ) -> list[DepartmentModel]:
        """Получение списка департаментов."""
        async with new_session() as session:
            result = await session.execute(
                select(DepartmentModel).where(DepartmentModel.parent_id == parent_id)
            )
            return list(result.scalars().all())

    @classmethod
    async def update(
        cls,
        departmnent_id: int,
        parent_id: int,
    ):
        """Назначение нового департамента."""
        async with new_session() as session:
            department = await session.get(
                DepartmentModel,
                departmnent_id,
            )
            if department is None:
                return None
            department.parent_id = parent_id
            session.add(department)
            await session.commit()
            await session.refresh(department)
            return department

    @classmethod
    async def delete(
        cls,
        department_id: int,
    ) -> None:
        """Удаление департамента."""
        async with new_session() as session:
            department = await session.get(
                DepartmentModel,
                department_id,
            )
            if department is None:
                return None
            await session.delete(department)
            await session.commit()
