"""Схемы сотрудников для API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from constant import MAX_LEGTH_STRING_FIELD, MIN_LENGH_STRING_FIELD


class SEmployees(BaseModel):
    """Схема для объекта сотрудник."""

    id: int
    department_id: int
    full_name: str = Field(
        min_length=MIN_LENGH_STRING_FIELD,
        max_length=MAX_LEGTH_STRING_FIELD,
    )
    position: str = Field(
        min_length=MIN_LENGH_STRING_FIELD,
        max_length=MAX_LEGTH_STRING_FIELD,
    )
    hired_at: Optional[datetime] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class SEmployeesCreate(BaseModel):
    """Схема для создания сотрудника."""

    full_name: str = Field(
        min_length=MIN_LENGH_STRING_FIELD,
        max_length=MAX_LEGTH_STRING_FIELD,
    )
    position: str = Field(
        min_length=MIN_LENGH_STRING_FIELD,
        max_length=MAX_LEGTH_STRING_FIELD,
    )
    hired_at: Optional[datetime] = None

    @field_validator("full_name", "position")
    @classmethod
    def strip_field(cls, value: str) -> str:
        return value.strip()


class SEmployeesResponse(SEmployees):
    """Ответ - созданный сотрудник."""

    pass
