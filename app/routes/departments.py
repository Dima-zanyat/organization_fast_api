from fastapi import APIRouter, status

from repositories.department import DepartmentRepository
from schemas.department import (
    SDepartmentResponse,
    SDepartmentCreate,
    SDepartmentTree,
    SDepartmentGet,
)

router = APIRouter(prefix="/departments")


@router.post(
    "/", response_model=SDepartmentResponse, status_code=status.HTTP_201_CREATED
)
async def create_department(data: SDepartmentCreate):
    """Создание департамента."""
    return await DepartmentRepository.create(data)


@router.get(
    "/{department_id}", response_model=SDepartmentTree, status_code=status.HTTP_200_OK
)
async def get_department_tree(
    id: int,
    data: SDepartmentGet,
):
    """Обновление департамента."""
    return await DepartmentRepository.get_subtree_by_depth(id, data.depth)
