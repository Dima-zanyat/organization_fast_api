"""Сервисный слой для работы с департаментами.

Модуль содержит бизнес-логику управления департаментами и их
иерархической структурой.

Основные возможности:
- создание департаментов;
- получение дерева департаментов заданной глубины;
- получение сотрудников департаментов;
- перемещение департаментов внутри дерева;
- предотвращение циклических ссылок;
- удаление департаментов и их поддеревьев;
- перенос сотрудников при удалении департамента.

Сервисный слой выступает посредником между API и репозиториями,
выполняя валидацию входных данных и проверку бизнес-правил
перед изменением данных в базе.
"""

from typing import Optional

from models.department import DepartmentModel
from models.employees import EmployeeModel
from repositories.department import DepartmentRepository
from repositories.employees import EmployeesRepository
from schemas.department import (
    SDepartmentCreate,
    SDepartmentGet,
    SDepartmentTree,
    SDepartmentUpdate,
    SDepartmentResponse,
    SDepartmentDelete,
    DeleteMode,
)
from schemas.empoyees import SEmployees


class DepartmentService:
    """
    Сервисный слой для работы с департаментами.

    Отвечает за реализацию бизнес-логики управления структурой
    департаментов организации.
    Методы:
        create_department:
            Создание нового департамента с проверкой существования
            родительского департамента.

        validate_department:
            Проверка существования департамента и возврат объекта
            модели при успешной валидации.

        get_employees:
            Получение списка сотрудников департамента и преобразование
            ORM-моделей в Pydantic-схемы.

        get_departments_ids:
            Извлечение списка идентификаторов из коллекции департаментов.

        get_detail_employee_tree:
            Построение дерева департаментов до указанной глубины
            с возможностью включения сотрудников каждого узла.

        update_department:
            Изменение родительского департамента с проверкой
            корректности структуры дерева и предотвращением циклов.

        delete_department:
            Удаление департамента:
            - CASCADE — удаление всего поддерева;
            - REASSIGN — перенос сотрудников в другой департамент
              перед удалением.
    """

    @classmethod
    async def create_department(
        cls,
        data: SDepartmentCreate,
    ) -> DepartmentModel:
        """Логика создания департамента."""
        if data.parent_id is not None:
            parent = await DepartmentRepository.get_by_id(department_id=data.parent_id)
            if parent is None:
                raise ValueError("Указанный департамент не найден.")

        return await DepartmentRepository.create(data)

    @classmethod
    def validate_department(
        cls,
        department: Optional[DepartmentModel],
    ) -> DepartmentModel:
        """Проверка на exist по department_id."""
        if department is None:
            raise ValueError("Объект не найден.")
        return department

    @classmethod
    async def get_emlpoyees(cls, department_id: int) -> list[SEmployees]:
        """Получение списка сотрудников."""
        employees_orm: list[EmployeeModel] = (
            await EmployeesRepository.list_by_department_id(department_id=department_id)
        )

        employees = [SEmployees.model_validate(employee) for employee in employees_orm]
        return employees

    @staticmethod
    def get_departmnets_ids(departments: list[DepartmentModel]) -> list[int]:
        """Метод для получения списка id департаментов."""
        return [department.id for department in departments]

    @classmethod
    async def get_detail_employee_tree(
        cls,
        department_id: int,
        data: SDepartmentGet,
    ) -> SDepartmentTree:
        """Получение дерева департаментов."""
        departments = await DepartmentRepository.get_subtree_by_depth(
            department_id=department_id,
            depth=data.depth,
        )

        departments_ids: list[int] = cls.get_departmnets_ids(departments)
        departments_by_id: dict[int, DepartmentModel] = {
            dep.id: dep for dep in departments
        }

        employees_by_department: dict[int, list[SEmployees]] = {
            dep_id: [] for dep_id in departments_ids
        }

        if data.include_employees:
            employees = await EmployeesRepository.list_by_departments_ids(
                department_ids=departments_ids
            )
            for employee in employees:
                employees_by_department.setdefault(employee.department_id, []).append(
                    SEmployees.model_validate(employee)
                )
        child_by_departments: dict[int | None, list[DepartmentModel]] = {}

        for department in departments:
            child_by_departments.setdefault(department.parent_id, []).append(department)

        def get_tree(department: DepartmentModel) -> SDepartmentTree:
            """Рекурсивное получение дерева."""
            node = SDepartmentTree.model_validate(department)
            node.employees = employees_by_department.get(department.id, [])
            node.children = [
                get_tree(child) for child in child_by_departments.get(department.id, [])
            ]
            return node

        root = departments_by_id.get(department_id)
        if root is None:
            raise ValueError("Департамент не найден")
        return get_tree(department=root)

    @classmethod
    async def update_department(
        cls,
        department_id: int,
        data: SDepartmentUpdate,
    ) -> SDepartmentResponse:
        """
        Перемещение департамента в другой родительский департамент.

        Проверяет существование департамента и нового родителя,
        а также предотвращает образование циклов в структуре дерева.
        """

        department = cls.validate_department(
            await DepartmentRepository.get_by_id(department_id)
        )

        if data.parent_id is None:
            raise ValueError("Необходимо указать parent_id")

        new_parent = cls.validate_department(
            await DepartmentRepository.get_by_id(data.parent_id)
        )

        if department.id == new_parent.id:
            raise ValueError("Нельзя сделать родителем самого себя.")

        subtree = await DepartmentRepository.get_full_subtree(department.id)

        subtree_ids = cls.get_departmnets_ids(subtree)

        if new_parent.id in subtree_ids:
            raise ValueError("Нельзя переместить департамент внутрь своего поддерева.")
        updated_department = await DepartmentRepository.update(
            department_id=department.id,
            parent_id=new_parent.id,
        )
        return SDepartmentResponse.model_validate(updated_department)

    @classmethod
    async def delete_department(
        cls,
        department_id: int,
        data: SDepartmentDelete,
    ):
        """Удаление департамента."""
        department_delete = cls.validate_department(
            await DepartmentRepository.get_by_id(department_id)
        )
        if data.mode == DeleteMode.CASCADE:
            departments = await DepartmentRepository.get_full_subtree(
                department_delete.id
            )
            departments_ids = cls.get_departmnets_ids(departments)
            await DepartmentRepository.delete_by_ids(departments_ids)
        if (
            data.mode == DeleteMode.REASSIGN
            and data.reassign_to_department_id is not None
        ):
            new_department_for_emploees = cls.validate_department(
                await DepartmentRepository.get_by_id(data.reassign_to_department_id)
            )
            emlpoyees = await EmployeesRepository.list_by_department_id(
                department_delete.id
            )
            emlpoyees_ids = [e.id for e in emlpoyees]
            await DepartmentRepository.reassign_employees_department(
                emlpoyees_ids,
                new_department_for_emploees.id,
            )
            await DepartmentRepository.delete_departement(department_delete.id)
