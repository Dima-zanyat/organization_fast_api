from sqlalchemy import select

from database import new_session
from schemas.empoyees import SEmployeesCreate
from models.employees import EmployeeModel
from models.department import DepartmentModel


class EmployeesRepository:
    """Репозиторий для сотрудников."""

    @classmethod
    async def create(
        cls,
        department_id: int,
        data: SEmployeesCreate,
    ) -> EmployeeModel:
        """Создать сотрудника в департаменте."""
        async with new_session() as session:
            department = await session.get(DepartmentModel, department_id)
            if department is None:
                raise ValueError("Департамент не найден")
            employee = EmployeeModel(**data.model_dump(), department_id=department_id)
            session.add(employee)
            await session.commit()
            await session.refresh(employee)
            return employee

    @classmethod
    async def list_by_department_id(
        cls,
        department_id: int,
    ) -> list[EmployeeModel]:
        """Возвращает список сотрудников."""
        async with new_session() as session:
            result = await session.execute(
                select(EmployeeModel)
                .where(EmployeeModel.department_id == department_id)
                .order_by(EmployeeModel.created_at)
            )
            return list(result.scalars().all())

    @classmethod
    async def list_by_departments_ids(
        cls,
        department_ids: list[int],
    ) -> list[EmployeeModel]:
        if not department_ids:
            return []
        async with new_session() as session:
            result = await session.execute(
                select(EmployeeModel)
                .where(EmployeeModel.department_id.in_(department_ids))
                .order_by(EmployeeModel.department_id, EmployeeModel.created_at)
            )
            return list(result.scalars().all())
