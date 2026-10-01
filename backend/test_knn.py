import asyncio

from elasticsearch import AsyncElasticsearch
from sentence_transformers import SentenceTransformer

from app.core.config import settings


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"

DOCUMENT_ID = "4d837077-5a2a-4f43-84f6-6a3ba194413b"

QUERY = "Tell me about her technical project experience"


async def test_knn():
    print()
    print("=" * 70)
    print("kNN SEMANTIC SEARCH TEST")
    print("=" * 70)

    print()
    print("Loading Nemotron embedding model...")

    embedding_model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    print("Embedding model loaded!")

    print()
    print(f"Query: {QUERY}")

    query_embedding = embedding_model.encode(
        QUERY,
        normalize_embeddings=False,
    )

    query_vector = query_embedding.tolist()

    es_client = AsyncElasticsearch(
        settings.elasticsearch_url
    )

    try:
        response = await es_client.search(
            index=INDEX_NAME,
            knn={
                "field": "embedding",
                "query_vector": query_vector,
                "k": 5,
                "num_candidates": 50,
                "filter": [
                    {
                        "term": {
                            "document_id": DOCUMENT_ID
                        }
                    }
                ],
            },
        )

        hits = response["hits"]["hits"]

        print()
        print(f"Results: {len(hits)}")
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


asyncio.run(test_knn())