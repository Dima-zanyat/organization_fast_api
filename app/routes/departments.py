from fastapi import APIRouter, status

from schemas.department import (
    SDepartmentResponse,
    SDepartmentCreate,
    SDepartmentTree,
    SDepartmentGet,
)
from services.department_service import DepartmentService

router = APIRouter(prefix="/departments")


@router.post(
    "/", response_model=SDepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(data: SDepartmentCreate):
    """Создание департамента."""
    return await DepartmentService.create_department(data)


@router.get(
    "/{department_id}", response_model=SDepartmentTree, status_code=status.HTTP_200_OK
)
async def get_department_tree(
    department_id: int,
    depth: int,
    include_employees: bool,
):
    """Обновление департамента."""
    data = SDepartmentGet(
        depth=depth,
        include_employees=include_employees,
    )
    return await DepartmentService.get_detail_employee_tree(
        department_id=department_id,
        data=data,
    )
