"""Схемы департамента для API."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, PositiveInt, model_validator

from app.constant import (
    MAX_LEGTH_STRING_FIELD,
    MIN_LENGH_STRING_FIELD,
    MAX_DIGIT_DEPTH,
    MIN_DIGIT_DEPTH,
    DEFAULT_DEPTH,
)
from app.schemas.empoyees import SEmployees


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

    name: str = Field(
        min_length=MIN_LENGH_STRING_FIELD,
        max_length=MAX_LEGTH_STRING_FIELD,
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


class SDepartmentGet(BaseModel):
    """Схема запроса на получение объекта."""

    depth: PositiveInt = Field(
        default=DEFAULT_DEPTH,
        ge=MIN_DIGIT_DEPTH,
        le=MAX_DIGIT_DEPTH,
    )
    include_employees: bool = True


class DeleteMode(str, Enum):
    """Перечисление с допустимыми значениями."""

    CASCADE = "cascade"
    REASSIGN = "reassign"


class SDepartmentDelete(BaseModel):
    """Схема запроса на удаление департамента."""

    mode: DeleteMode = Field(description="режим удаления только cascade или reassign")
    reassign_to_department_id: PositiveInt | None = None

    @model_validator(mode="after")
    def validate_reassign_department(self) -> "SDepartmentDelete":
        """Проверка значения reassign_to_department_id при моде reassign"""

        if self.mode == DeleteMode.REASSIGN and self.reassign_to_department_id is None:
            raise ValueError(
                "Для режима REASSIGN необходимо указать reassign_to_department_id."
            )
        return self


class SDepartmentTree(SDepartmentBase):
    """Схема запроса для детальной инфорамции."""

    employees: list[SEmployees] = Field(default_factory=list)
    children: list["SDepartmentTree"] = Field(default_factory=list)


SDepartmentTree.model_rebuild()
