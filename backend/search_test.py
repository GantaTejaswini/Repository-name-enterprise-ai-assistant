import asyncio

from app.core.elasticsearch import es_client

INDEX_NAME = "document_chunks"


async def main():
    try:
        response = await es_client.search(
            index=INDEX_NAME,
            query={
                "match": {
                    "content": "retrieval augmented generation"
                }
            }
        )

        print("Total hits:", response["hits"]["total"])
        print()

        for hit in response["hits"]["hits"]:
            print("Score:", hit["_score"])
            print("Document ID:", hit["_source"]["document_id"])
            print("Content:", hit["_source"]["content"])
            print("-" * 80)

    finally:
        await es_client.close()


asyncio.run(main())