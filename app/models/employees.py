""" "Файл модели сотрудников."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from constant import MAX_LEGTH_STRING_FIELD
from database import Model
from models.department import DepartmentModel


class EmployeeModel(Model):
    """ОРМ модель для сотрудников."""

    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="cascade"),
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(MAX_LEGTH_STRING_FIELD),
        nullable=False,
    )
    position: Mapped[str] = mapped_column(
        String(MAX_LEGTH_STRING_FIELD),
        nullable=False,
    )
    hired_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    department: Mapped["DepartmentModel"] = relationship(
        "DepartmentModel",
        back_populates="employees",
    )
