import asyncio

from sqlalchemy import text

from app.core.database import engine


async def main():
    query = text(
        """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND data_type LIKE '%timestamp%'
        ORDER BY table_name, column_name;
        """
    )

    async with engine.connect() as connection:
        result = await connection.execute(query)

        for row in result:
            print(
                f"{row.table_name}.{row.column_name}"
                f" -> {row.data_type}"
            )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())