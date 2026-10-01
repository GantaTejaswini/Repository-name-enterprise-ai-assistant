import asyncio

from elasticsearch import AsyncElasticsearch

from app.core.config import settings


INDEX_NAME = "document_chunks"

DOCUMENT_ID = "4d837077-5a2a-4f43-84f6-6a3ba194413b"

QUERY = "What projects has Tejaswini worked on?"


async def test_bm25():
    es_client = AsyncElasticsearch(
        settings.elasticsearch_url
    )

    try:
        response = await es_client.search(
            index=INDEX_NAME,
            query={
                "bool": {
                    "must": [
                        {
                            "match": {
                                "content": QUERY
                            }
                        }
                    ],
                    "filter": [
                        {
                            "term": {
                                "document_id": DOCUMENT_ID
                            }
                        }
                    ],
                }
            },
            size=5,
        )

        hits = response["hits"]["hits"]

        print()
        print("=" * 70)
        print("BM25 SEARCH TEST")
        print("=" * 70)
        print(f"Query       : {QUERY}")
        print(f"Results     : {len(hits)}")
        print()

        for rank, hit in enumerate(hits, start=1):
            source = hit["_source"]

            print(f"Rank        : {rank}")
            print(f"Score       : {hit['_score']}")
            print(f"Chunk ID    : {source['chunk_id']}")
            print(f"Page        : {source['page_number']}")
            print(
                f"Content     : "
                f"{source['content'][:300]}"
            )
            print("-" * 70)

        print("=" * 70)

    finally:
        await es_client.close()


asyncio.run(test_bm25())