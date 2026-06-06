"""Ендпоинты для работы с сотрудниками."""

from fastapi import APIRouter, status

from app.schemas.empoyees import SEmployeesCreate, SEmployeesResponse
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/departments")


@router.post(
    "/{department_id}/employees",
    status_code=status.HTTP_201_CREATED,
    response_model=SEmployeesResponse,
)
async def create_employee(
    department_id: int,
    data: SEmployeesCreate,
):
    """Создание сотрудника в департаменте."""
    return await EmployeeService.create_employee(
        department_id=department_id,
        data=data,
    )
