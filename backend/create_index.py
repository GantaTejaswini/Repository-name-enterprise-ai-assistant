import asyncio

from app.core.elasticsearch import es_client


INDEX_NAME = "document_chunks"


INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "document_id": {
                "type": "keyword"
            },
            "tenant_id": {
                "type": "keyword"
            },
            "filename": {
                "type": "keyword"
            },
            "page_number": {
                "type": "integer"
            },
            "chunk_id": {
                "type": "keyword"
            },
            "content": {
                "type": "text"
            },
            "embedding": {
                "type": "dense_vector",
                "dims": 2048,
                "index": True,
                "similarity": "cosine"
            },
            "metadata": {
                "type": "object"
            }
        }
    }
}


async def main():
    exists = await es_client.indices.exists(
        index=INDEX_NAME
    )

    if exists:
        print(f"Index already exists: {INDEX_NAME}")
    else:
        await es_client.indices.create(
            index=INDEX_NAME,
            body=INDEX_MAPPING
        )
        print(f"Index created: {INDEX_NAME}")

    await es_client.close()


asyncio.run(main())