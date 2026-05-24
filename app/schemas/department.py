"""Схемы департамента для API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from constant import MAX_LEGTH_STRING_FIELD, MIN_LENGH_STRING_FIELD
from schemas.empoyees import SEmployees


class SDepartmentBase(BaseModel):
    """Схема для объекта департамент."""

    id: int
    name: str
    parent_id: Optional[int] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class SDepartmentBaseCreateOrUpdate(BaseModel):
    """Базовая схема для создания или обновления."""

    name: Optional[str] = Field(
        min_length=MIN_LENGH_STRING_FIELD,
        max_length=MAX_LEGTH_STRING_FIELD,
        default=None,
    )
    parent_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def strip_field(cls, value: str) -> str:
        return value.strip()


class SDepartmentResponse(SDepartmentBase):
    """Схема ответа на запрос."""


class SDepartmentCreate(SDepartmentBaseCreateOrUpdate):
    """Схема на запрос создания депатамента."""


class SDepartmentUpdate(SDepartmentBaseCreateOrUpdate):
    """Схема на запрос обновления департамента."""


class SDepartmentTree(SDepartmentBase):
    """Схема запроса для детальной инфорамции."""

    employees: list[SEmployees] = Field(default_factory=list)
    children: list["SDepartmentTree"] = Field(default_factory=list)


SDepartmentTree.model_rebuild()
