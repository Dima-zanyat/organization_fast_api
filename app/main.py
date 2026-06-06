from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
