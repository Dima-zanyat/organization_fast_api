"""Ендпоинты департаметна."""

from fastapi import APIRouter, status

from schemas.department import (
    SDepartmentResponse,
    SDepartmentCreate,
    SDepartmentTree,
    SDepartmentGet,
    SDepartmentUpdate,
    SDepartmentDelete,
    DeleteMode,
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
    depth: int = 1,
    include_employees: bool = True,
):
    """Получение дерева департамента с сотрудниками."""

    data = SDepartmentGet(
        depth=depth,
        include_employees=include_employees,
    )
    return await DepartmentService.get_detail_employee_tree(
        department_id=department_id,
        data=data,
    )


@router.patch(
    "/{department_id}",
    response_model=SDepartmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_department(
    department_id: int,
    data: SDepartmentUpdate,
):
    """Обновляет департамент, включая смену родительского департамента."""

    return await DepartmentService.update_department(department_id, data)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    mode: DeleteMode,
    reassign_to_department_id: int,
):
    data = SDepartmentDelete(
        mode=mode,
        reassign_to_department_id=reassign_to_department_id,
    )
    await DepartmentService.delete_department(
        department_id=department_id,
        data=data,
    )
    return None
