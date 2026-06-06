""""""

from app.schemas.empoyees import SEmployeesCreate, SEmployeesResponse
from app.services.department_service import DepartmentService
from app.repositories.employees import EmployeesRepository
from app.repositories.department import DepartmentRepository


class EmployeeService:
    """
    Сервисный слой для работы с сотрудниками.

    Отвечает за реализацию бизнес-логики управления сотрудниквов
    организации.
    """

    @classmethod
    async def create_employee(
        cls,
        department_id: int,
        data: SEmployeesCreate,
    ) -> SEmployeesResponse:
        """Метод для создания сотрудников."""
        department = await DepartmentRepository.get_by_id(department_id)
        DepartmentService.validate_department(department)

        employee = await EmployeesRepository.create(department_id, data)
        return SEmployeesResponse.model_validate(employee)
