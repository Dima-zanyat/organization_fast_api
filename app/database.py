"""Конфигуратор базы данных и менеджер сессии."""

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)
new_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=True,
)


async def get_session():
    """Функция-зависимость для получения сессии БД."""
    async with new_session() as session:
        yield session


class Model(DeclarativeBase):
    """Базовый класс моделей."""
