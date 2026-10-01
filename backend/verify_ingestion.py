import asyncio

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


async def main():

    print("=" * 80)
    print("DOCUMENT INGESTION VERIFICATION")
    print("=" * 80)

    async with AsyncSessionLocal() as db:

        document_result = await db.execute(
            select(Document)
            .order_by(Document.created_at.desc())
            .limit(1)
        )

        document = document_result.scalar_one_or_none()

        if document is None:
            print("No document found.")
            return

        chunk_result = await db.execute(
            select(func.count(DocumentChunk.id))
            .where(
                DocumentChunk.document_id
                == document.id
            )
        )

        chunk_count = chunk_result.scalar_one()

        print()
        print(f"Document ID : {document.id}")
        print(f"Filename    : {document.filename}")
        print(f"Tenant ID   : {document.tenant_id}")
        print(f"Status      : {document.status}")
        print(f"Chunk count : {chunk_count}")

    print()
    print("=" * 80)
    print("VERIFICATION FINISHED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())