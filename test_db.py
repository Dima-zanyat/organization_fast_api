import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()
url = os.getenv("DATABASE_URL")


async def check():
    print(f"Попытка подключения к: {url}")
    engine = create_async_engine(url, pool_pre_ping=True)

    try:
        async with engine.connect() as conn:
            # Используем прямой SQL-запрос для получения списка таблиц в Postgres
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
            """)
            result = await conn.execute(query)
            tables = [row[0] for row in result.fetchall()]

            print("\n=== РЕАЛЬНЫЕ ТАБЛИЦЫ В БАЗЕ ИЗ .ENV ===")
            print(tables)
            print("=======================================\n")

    except Exception as e:
        print(type(e))
        print(repr(e))
        print(f"\nПроизошла ошибка при выполнении запроса: {e}\n")
    finally:
        # Даем драйверу время корректно закрыть все пулы соединений
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check())
