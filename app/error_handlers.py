"""Файл обработки ошибок."""

from http import HTTPStatus


class AppException(Exception):
    """Базовое исключение приложения."""

    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class DepartmentNotFoundException(AppException):
    """Департамент не найден."""

    status_code = HTTPStatus.NOT_FOUND


class ValidationException(AppException):
    """Ошибка бизнес-валидации."""

    status_code = HTTPStatus.BAD_REQUEST


class InvalidDepartmentMoveException(AppException):
    """Некорректное перемещение департамента."""

    status_code = HTTPStatus.CONFLICT
