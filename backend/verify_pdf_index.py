import asyncio

from app.core.elasticsearch import es_client


INDEX_NAME = "document_chunks"
DOCUMENT_ID = "resume-demo-001"


async def main():

    print("Searching indexed resume chunks...")

    response = await es_client.search(
        index=INDEX_NAME,
        query={
            "term": {
                "document_id": DOCUMENT_ID
            }
        },
        size=20,
        sort=[
            {
                "page_number": {
                    "order": "asc"
                }
            }
        ],
    )

    hits = response["hits"]["hits"]

    print()
    print("Resume chunks found:", len(hits))
    print()

    for hit in hits:

        source = hit["_source"]

        print("=" * 80)
        print("Chunk ID:", source["chunk_id"])
        print("Page:", source["page_number"])
        print("Filename:", source["filename"])
        print("Embedding dimensions:", len(source["embedding"]))
        print("Content:")
        print(source["content"])
        print()

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())