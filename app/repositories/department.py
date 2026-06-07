"""Файл для репозитория подразделений."""

from typing import Optional

from fastapi import Depends
from sqlalchemy import select, literal, update, delete
from sqlalchemy.orm import aliased, Session


from app.constant import REDUCT_NUMBER_RECURSION
from app.schemas.department import SDepartmentCreate
from app.models.department import DepartmentModel
from app.models.employees import EmployeeModel
from app.exceptions import DepartmentNotFoundException


class DepartmentRepository:
    """Репозиторий для CRUD операций."""

    @classmethod
    async def create(
        cls,
        data: SDepartmentCreate,
        session,
    ) -> DepartmentModel:
        """Создание департамента."""
        department_data = data.model_dump()
        department = DepartmentModel(**department_data)
        session.add(department)
        await session.commit()
        await session.refresh(department)
        return department

    @classmethod
    async def get_by_id(
        cls,
        department_id: int,
        session,
    ) -> Optional[DepartmentModel]:
        """Получение объекта департамента."""
        department = await session.get(
            DepartmentModel,
            department_id,
        )
        return department

    @staticmethod
    def build_subtree_conditions(departments_alias, tree_cte, params=None):
        """Построение условий для рекурсивного обхода дерева департаментов."""

        if params:
            if "depth" in params:
                depth = params["depth"]
                return [
                    departments_alias.parent_id == tree_cte.c.id,
                    tree_cte.c.level < depth - REDUCT_NUMBER_RECURSION,
                ]
        if params is None:
            return [
                departments_alias.parent_id == tree_cte.c.id,
            ]

    @staticmethod
    def build_root_cte(department_id: int):
        """Создание корневого CTE для построения дерева департаментов."""

        return (
            select(
                DepartmentModel.id,
                DepartmentModel.name,
                DepartmentModel.parent_id,
                DepartmentModel.created_at,
                literal(0).label("level"),
            )
            .where(DepartmentModel.id == department_id)
            .cte("department_cte", recursive=True)
        )

    @staticmethod
    def build_recursive_subtree_query(departments_alias, tree_cte, conditions):
        """Создание рекурсивной части запроса для обхода дерева департаментов."""

        return select(
            departments_alias.id,
            departments_alias.name,
            departments_alias.parent_id,
            departments_alias.created_at,
            (tree_cte.c.level + 1).label("level"),
        ).where(*conditions)

    @classmethod
    async def get_subtree(
        cls,
        department_id: int,
        session,
        params=None,
    ) -> list[DepartmentModel]:
        """Получени поддерева департамента с возможностью выбора параметра."""
        tree_cte = cls.build_root_cte(department_id=department_id)
        departments_alias = aliased(DepartmentModel, name="dep")
        condition = cls.build_subtree_conditions(departments_alias, tree_cte, params)
        recursive_query = cls.build_recursive_subtree_query(
            departments_alias=departments_alias,
            tree_cte=tree_cte,
            conditions=condition,
        )
        final_tree_query = tree_cte.union_all(recursive_query)
        query_result = await session.execute(select(final_tree_query))

        return list(query_result.scalars().all())

    @classmethod
    async def get_subtree_by_depth(
        cls,
        department_id: int,
        depth: int,
        session,
    ) -> list[DepartmentModel]:
        """Получение всех дпартаментов до указанной глубины."""
        params = {"depth": depth}
        return await cls.get_subtree(
            department_id=department_id,
            params=params,
            session=session,
        )

    @classmethod
    async def get_full_subtree(
        cls,
        department_id: int,
        session,
    ) -> list[DepartmentModel]:
        """Получение полного поддерева департамента без ограничения глубины."""

        return await cls.get_subtree(department_id=department_id, session=session)

    @classmethod
    async def list_by_parent_id(
        cls,
        parent_id: int,
        session,
    ) -> list[DepartmentModel]:
        """Получение списка департаментов."""

        result = await session.execute(
            select(DepartmentModel).where(DepartmentModel.parent_id == parent_id)
        )
        return list(result.scalars().all())

    @classmethod
    async def update(
        cls,
        department_id: int,
        parent_id: int,
        name: str,
        session,
    ) -> DepartmentModel:
        """Назначение нового департамента."""
        department = await session.get(
            DepartmentModel,
            department_id,
        )
        if department is None:
            raise DepartmentNotFoundException("Департамента с таким id не существует.")
        department.parent_id = parent_id
        department.name = name
        session.add(department)
        await session.commit()
        await session.refresh(department)
        return department

    @classmethod
    async def reassign_employees_department(
        cls,
        emlpoyees_ids: list[int],
        new_department: int,
        session,
    ) -> None:
        """Перемещеие сотрудников в другой департамент."""
        await session.execute(
            update(EmployeeModel)
            .where(EmployeeModel.id.in_(emlpoyees_ids))
            .values(department_id=new_department)
        )
        await session.commit()

    @classmethod
    async def delete_departement(
        cls,
        departament_id: int,
        session,
    ) -> None:
        """Удаление одного департамента."""
        await session.execute(
            delete(DepartmentModel).where(DepartmentModel.id == departament_id)
        )
        await session.commit()

    @classmethod
    async def delete_by_ids(
        cls,
        departament_ids: list[int],
        session,
    ) -> None:
        """Каскадное удаление департамента."""
        await session.execute(
            delete(DepartmentModel).where(DepartmentModel.id.in_(departament_ids))
        )
        await session.commit()
