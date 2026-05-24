"""Конфигуратор базы данных и менеджер сессии."""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from constant import DATABASE_URL

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


class Model(DeclarativeBase):
    """Базовый класс моделей."""
