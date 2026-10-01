import asyncio
from sqlalchemy import text
from app.core.database import engine


async def main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("PostgreSQL:", result.scalar_one())

    await engine.dispose()


asyncio.run(main())