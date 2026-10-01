import asyncio

from elasticsearch import AsyncElasticsearch
from sentence_transformers import SentenceTransformer
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"

DOCUMENT_ID = "4d837077-5a2a-4f43-84f6-6a3ba194413b"


async def index_document_embeddings():
    print()
    print("=" * 70)
    print("NEMOTRON EMBEDDING + ELASTICSEARCH INDEXING")
    print("=" * 70)

    print()
    print("Loading Nemotron embedding model...")

    embedding_model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    print("Nemotron embedding model loaded!")

    print()
    print("Connecting to PostgreSQL...")

    async with AsyncSessionLocal() as db:

        result = await db.execute(
            select(DocumentChunk, Document)
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .where(
                DocumentChunk.document_id == DOCUMENT_ID
            )
        )

        rows = result.all()

    print(f"Retrieved {len(rows)} chunks from PostgreSQL.")

    if not rows:
        print("No chunks found.")
        return

    print()
    print("Generating embeddings...")

    es_client = AsyncElasticsearch(
        settings.elasticsearch_url
    )

    try:
        for index, (chunk, document) in enumerate(
            rows,
            start=1,
        ):
            print(
                f"Processing chunk {index}/{len(rows)}..."
            )

            embedding = embedding_model.encode(
                chunk.content,
                normalize_embeddings=False,
            )

            query_vector = embedding.tolist()

            document_body = {
                "document_id": document.id,
                "tenant_id": document.tenant_id,
                "filename": document.filename,
                "page_number": chunk.page_number,
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "embedding": query_vector,
                "metadata": {
                    "source": "uploaded_pdf",
                    "document_type": "pdf",
                },
            }

            await es_client.index(
                index=INDEX_NAME,
                id=chunk.id,
                document=document_body,
            )

            print(
                f"Indexed chunk {index}: "
                f"{chunk.chunk_id}"
            )

        await es_client.indices.refresh(
            index=INDEX_NAME
        )

        print()
        print("=" * 70)
        print("INDEXING COMPLETE")
        print("=" * 70)
        print(f"Document ID : {DOCUMENT_ID}")
        print(f"Chunks      : {len(rows)}")
        print(f"Index       : {INDEX_NAME}")
        print("=" * 70)

    finally:
        await es_client.close()


asyncio.run(index_document_embeddings())