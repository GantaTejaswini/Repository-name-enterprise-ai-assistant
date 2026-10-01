import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.document_chunk import DocumentChunk


async def verify_chunks():

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(DocumentChunk)
        )

        chunks = result.scalars().all()

        print()
        print("=" * 70)
        print("ALL POSTGRESQL DOCUMENT CHUNKS")
        print("=" * 70)
        print(f"Total chunks: {len(chunks)}")
        print()

        for chunk in chunks:

            print(f"Database ID : {chunk.id}")
            print(f"Document ID : {chunk.document_id}")
            print(f"Chunk ID    : {chunk.chunk_id}")
            print(f"Page        : {chunk.page_number}")
            print(f"Content     : {chunk.content[:200]}")
            print("-" * 70)

        print("=" * 70)


asyncio.run(verify_chunks())