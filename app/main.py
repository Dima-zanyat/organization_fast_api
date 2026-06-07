from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.error_handlers import AppException
from app.routes.departments import router as dep_routers
from app.routes.employees import router as emp_routers

app = FastAPI(
    title="Department_API",
    version="1.0.0",
)
app.include_router(dep_routers)
app.include_router(emp_routers)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Проверка доступности сервиса."""
    return {"status": "ok"}


@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    error: AppException,
):
    """Обработчик кастомных ошибок."""
    return JSONResponse(
        content={"message": error.message},
        status_code=error.status_code,
    )
