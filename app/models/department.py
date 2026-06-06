"""Модель департамента."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, ForeignKey, String, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constant import MAX_LEGTH_STRING_FIELD
from app.database import Model


class DepartmentModel(Model):
    """ОРМ модель подразделения."""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(MAX_LEGTH_STRING_FIELD),
        nullable=False,
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    parent: Mapped[Optional["DepartmentModel"]] = relationship(
        "DepartmentModel",
        remote_side=[id],
        back_populates="sub_departments",
    )

    sub_departments: Mapped[list["DepartmentModel"]] = relationship(
        "DepartmentModel",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    employees: Mapped[list["EmployeeModel"]] = relationship(
        "EmployeeModel",
        back_populates="department",
    )
    __table_args__ = (
        UniqueConstraint(
            "name",
            "parent_id",
            name="uq_department_parent_name",
        ),
    )
