"""
Сервисный слой для управления сотрудниками.

Данный модуль содержит бизнес-логику для работы с сущностями сотрудников,
включая их создание, валидацию связанных департаментов и взаимодействие
с репозиториями.
"""

from app.schemas.empoyees import SEmployeesCreate, SEmployeesResponse
from app.services.department_service import DepartmentService
from app.repositories.employees import EmployeesRepository
from app.repositories.department import DepartmentRepository


class EmployeeService:
    """
    Создает нового сотрудника в указанном департаменте.

    Перед созданием сотрудника метод выполняет обязательную валидацию
    существования и доступности выбранного департамента. В случае успешной
    проверки данные сохраняются в базу данных.

    Args:
        department_id (int): Уникальный идентификатор департамента.
        data (SEmployeesCreate): Схема валидными данными для создания сотрудника.
        session (AsyncSession): Асинхронная сессия подключения к базе данных.

    Raises:
        AppException: Если департамент не найден или не прошел валидацию.

    Returns:
        SEmployeesResponse: Схема  полной информации созданном сотруднике.
    """

    @classmethod
    async def create_employee(
        cls,
        department_id: int,
        data: SEmployeesCreate,
        session,
    ) -> SEmployeesResponse:
        """Метод для создания сотрудников."""
        department = await DepartmentRepository.get_by_id(
            department_id=department_id,
            session=session,
        )
        DepartmentService.validate_department(department)

        employee = await EmployeesRepository.create(
            department_id=department_id,
            data=data,
            session=session,
        )
        return SEmployeesResponse.model_validate(employee)
