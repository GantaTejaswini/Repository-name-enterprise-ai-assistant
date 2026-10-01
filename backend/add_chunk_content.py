import asyncio

from sqlalchemy import text

from app.core.database import engine


async def add_chunk_content():

    async with engine.begin() as connection:

        await connection.execute(
            text(
                """
                ALTER TABLE document_chunks
                ADD COLUMN IF NOT EXISTS content TEXT
                """
            )
        )

    print("content column added successfully!")


asyncio.run(add_chunk_content())