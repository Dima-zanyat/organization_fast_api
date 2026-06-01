from fastapi import FastAPI

from routes.departments import router as dep_routers
from routes.employees import router as emp_routers

app = FastAPI(
    title="Department_API",
    version="1.0.0",
)
app.include_router(dep_routers)
app.include_router(emp_routers)
