import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="organization",
        host="localhost",
        port=5432,
    )

    value = await conn.fetchval("SELECT 1")
    print(value)

    await conn.close()


asyncio.run(main())
