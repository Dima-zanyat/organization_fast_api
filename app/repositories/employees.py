"""
Репозиторий для работы с сотрудниками.

Модуль содержит слой доступа к данным (Data Access Layer),
отвечающий за выполнение CRUD-операций над сущностью сотрудников.

Предоставляет методы для:
- создания сотрудников;
- получения сотрудников по департаменту;
- получения сотрудников по списку департаментов;
- обновления привязки сотрудников к департаментам.

Репозиторий не содержит бизнес-логики и не выполняет валидацию
входных данных — он работает исключительно с базой данных через ORM.
"""

from sqlalchemy import select

from app.schemas.empoyees import SEmployeesCreate
from app.models.employees import EmployeeModel
from app.models.department import DepartmentModel


class EmployeesRepository:
    """
    Репозиторий для работы с сущностью сотрудников.

    Предоставляет низкоуровневый доступ к данным сотрудников через ORM
    и отвечает за выполнение операций чтения и записи в базе данных.

    Класс реализует слой доступа к данным (Data Access Layer) и не содержит
    бизнес-логики или проверок существования связанных сущностей (например,
    департаментов) — это обязанность сервисного слоя.

    Методы:
        create:
            Создание нового сотрудника в указанном департаменте.
            Принимает данные сотрудника и department_id, сохраняет запись в БД
            и возвращает созданную ORM-модель.

        list_by_department_id:
            Получение списка сотрудников, принадлежащих одному департаменту.
            Возвращает отсортированный по дате создания список сотрудников.

        list_by_departments_ids:
            Получение сотрудников сразу из нескольких департаментов.
            Используется для построения дерева департаментов и агрегированных
            выборок. Возвращает сотрудников, отсортированных по департаменту
            и дате создания.

        update_departments_for_employyes:
            Перенос сотрудников в другой департамент.
            Обновляет связь сотрудников с департаментом (relationship-level операция).
            Используется при перемещении или удалении департамента с режимом REASSIGN.
    """

    @classmethod
    async def create(
        cls,
        department_id: int,
        data: SEmployeesCreate,
        session,
    ) -> EmployeeModel:
        """Создать сотрудника в департаменте."""
        employee = EmployeeModel(**data.model_dump(), department_id=department_id)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        return employee

    @classmethod
    async def list_by_department_id(
        cls,
        department_id: int,
        session,
    ) -> list[EmployeeModel]:
        """Возвращает список сотрудников."""
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
        session,
    ) -> list[EmployeeModel]:
        if not department_ids:
            return []
        result = await session.execute(
            select(EmployeeModel)
            .join(DepartmentModel, EmployeeModel.department_id == DepartmentModel.id)
            .where(DepartmentModel.id.in_(department_ids))
            .order_by(EmployeeModel.department_id, EmployeeModel.created_at)
        )
        return list(result.scalars().all())
