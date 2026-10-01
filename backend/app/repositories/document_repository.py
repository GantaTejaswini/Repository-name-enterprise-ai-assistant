from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class DocumentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        tenant_id: str,
        filename: str,
    ) -> Document:

        document = Document(
            tenant_id=tenant_id,
            filename=filename,
            status="uploaded",
        )

        self.db.add(document)

        await self.db.commit()

        await self.db.refresh(document)

        return document

    async def get_by_id(
        self,
        document_id: str,
        tenant_id: str,
    ) -> Document | None:

        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.tenant_id == tenant_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        tenant_id: str,
    ) -> list[Document]:

        result = await self.db.execute(
            select(Document)
            .where(
                Document.tenant_id == tenant_id
            )
            .order_by(
                Document.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        document_id: str,
        tenant_id: str,
        status: str,
    ) -> Document | None:

        document = await self.get_by_id(
            document_id=document_id,
            tenant_id=tenant_id,
        )

        if document is None:
            return None

        document.status = status

        await self.db.commit()

        await self.db.refresh(document)

        return document

    async def create_chunks(
        self,
        document_id: str,
        chunks: list[dict],
    ) -> list[DocumentChunk]:

        document_chunks = []

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            document_chunk = DocumentChunk(
                document_id=document_id,
                chunk_id=(
                    f"{document_id}-chunk-{index}"
                ),
                page_number=chunk["page_number"],
                content=chunk["content"],
            )

            self.db.add(document_chunk)

            document_chunks.append(
                document_chunk
            )

        await self.db.commit()

        for document_chunk in document_chunks:
            await self.db.refresh(
                document_chunk
            )

        return document_chunks

    async def delete(
        self,
        document_id: str,
        tenant_id: str,
    ) -> Document | None:

        document = await self.get_by_id(
            document_id=document_id,
            tenant_id=tenant_id,
        )

        if document is None:
            return None

        await self.db.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id
                == document.id
            )
        )

        await self.db.delete(document)

        await self.db.commit()

        return document