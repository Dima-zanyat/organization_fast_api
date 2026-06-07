"""Обработчики ошибок."""

from fastapi.responses import JSONResponse

from app.exceptions import AppException
from app.main import app


@app.exception_handler(AppException)
async def app_exception_handler(
    error: AppException,
):
    """Обработчик кастомных ошибок."""
    return JSONResponse(
        content={"message": error.message},
        status_code=error.status_code,
    )
