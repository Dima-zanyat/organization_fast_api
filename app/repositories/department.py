"""Файл для репозитория подразделений."""

from typing import Optional

from sqlalchemy import select, literal, update, delete
from sqlalchemy.orm import aliased


from constant import REDUCT_NUMBER_RECURSION, INCREASE_NUMBER
from database import new_session
from schemas.department import SDepartmentCreate, SDepartmentResponse
from models.department import DepartmentModel
from models.employees import EmployeeModel


class DepartmentRepository:
    """Репозиторий для CRUD операций."""

    @classmethod
    async def create(
        cls,
        data: SDepartmentCreate,
    ) -> DepartmentModel:
        """Создание департамента."""
        async with new_session() as session:
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
    ) -> Optional[DepartmentModel]:
        """Получение объекта департамента."""
        async with new_session() as session:
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
        params=None,
    ) -> list[DepartmentModel]:
        """Получени поддерева департамента с возможностью выбора параметра."""

        async with new_session() as session:
            tree_cte = cls.build_root_cte(department_id=department_id)
            departments_alias = aliased(DepartmentModel, name="dep")
            condition = cls.build_subtree_conditions(
                departments_alias, tree_cte, params
            )
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
    ) -> list[DepartmentModel]:
        """Получение всех дпартаментов до указанной глубины."""
        params = {"depth": depth}
        return await cls.get_subtree(
            department_id=department_id,
            params=params,
        )

    @classmethod
    async def get_full_subtree(
        cls,
        department_id: int,
    ) -> list[DepartmentModel]:
        """Получение полного поддерева департамента без ограничения глубины."""

        return await cls.get_subtree(
            department_id=department_id,
        )

    @classmethod
    async def list_by_parent_id(
        cls,
        parent_id: int,
    ) -> list[DepartmentModel]:
        """Получение списка департаментов."""
        async with new_session() as session:
            result = await session.execute(
                select(DepartmentModel).where(DepartmentModel.parent_id == parent_id)
            )
            return list(result.scalars().all())

    @classmethod
    async def update(
        cls,
        department_id: int,
        parent_id: int,
    ) -> DepartmentModel:
        """Назначение нового департамента."""
        async with new_session() as session:
            department = await session.get(
                DepartmentModel,
                department_id,
            )
            if department is None:
                raise ValueError("Департамента с таким id не существует.")
            department.parent_id = parent_id
            session.add(department)
            await session.commit()
            await session.refresh(department)
            return department

    @classmethod
    async def reassign_employees_department(
        cls,
        emlpoyees_ids: list[int],
        new_department: int,
    ) -> None:
        """Перемещеие сотрудников в другой департамент."""
        async with new_session() as session:
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
    ) -> None:
        """Удаление одного департамента."""
        async with new_session() as session:
            await session.execute(
                delete(DepartmentModel).where(DepartmentModel.id == departament_id)
            )
            await session.commit()

    @classmethod
    async def delete_by_ids(
        cls,
        departament_ids: list[int],
    ) -> None:
        """Каскадное удаление департамента."""
        async with new_session() as session:
            await session.execute(
                delete(DepartmentModel).where(DepartmentModel.id.in_(departament_ids))
            )
            await session.commit()
