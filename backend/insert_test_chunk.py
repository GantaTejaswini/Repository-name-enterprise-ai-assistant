import asyncio

from app.core.elasticsearch import es_client


INDEX_NAME = "document_chunks"


TEST_CHUNK = {
    "document_id": "test-document-001",
    "tenant_id": "tenant-demo",
    "filename": "enterprise_ai_guide.pdf",
    "page_number": 1,
    "chunk_id": "chunk-001",
    "content": (
        "Enterprise AI assistants use retrieval augmented generation "
        "to retrieve relevant information from documents before "
        "generating an answer with a large language model."
    ),
    # Temporary non-zero vector for testing Elasticsearch storage.
    "embedding": [0.01] * 2048,
    "metadata": {
        "source": "test",
        "document_type": "pdf"
    }
}


async def main():
    try:
        response = await es_client.index(
            index=INDEX_NAME,
            id=TEST_CHUNK["chunk_id"],
            document=TEST_CHUNK
        )

        print("Document indexed:", response["result"])

        await es_client.indices.refresh(
            index=INDEX_NAME
        )

    finally:
        await es_client.close()


asyncio.run(main())