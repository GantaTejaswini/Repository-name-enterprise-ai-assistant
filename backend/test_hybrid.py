import asyncio

from elasticsearch import AsyncElasticsearch
from sentence_transformers import SentenceTransformer

from app.core.config import settings


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"

DOCUMENT_ID = "4d837077-5a2a-4f43-84f6-6a3ba194413b"

QUERY = "Tell me about her technical project experience"

TOP_K = 5
RANK_CONSTANT = 20


async def test_hybrid():
    print()
    print("=" * 70)
    print("HYBRID BM25 + kNN + RRF TEST")
    print("=" * 70)

    print()
    print("Loading Nemotron embedding model...")

    embedding_model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    print("Embedding model loaded!")

    query_embedding = embedding_model.encode(
        QUERY,
        normalize_embeddings=False,
    )

    query_vector = query_embedding.tolist()

    es_client = AsyncElasticsearch(
        settings.elasticsearch_url
    )

    try:
        # --------------------------------------------------
        # BM25 SEARCH
        # --------------------------------------------------

        bm25_response = await es_client.search(
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
            size=TOP_K,
        )

        # --------------------------------------------------
        # kNN SEARCH
        # --------------------------------------------------

        knn_response = await es_client.search(
            index=INDEX_NAME,
            knn={
                "field": "embedding",
                "query_vector": query_vector,
                "k": TOP_K,
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

        # --------------------------------------------------
        # RRF FUSION
        # --------------------------------------------------

        combined_results = {}

        for rank, hit in enumerate(
            bm25_response["hits"]["hits"],
            start=1,
        ):
            document_id = hit["_id"]

            if document_id not in combined_results:
                combined_results[document_id] = {
                    "source": hit["_source"],
                    "bm25_rank": None,
                    "knn_rank": None,
                    "bm25_score": None,
                    "knn_score": None,
                    "rrf_score": 0.0,
                }

            combined_results[document_id]["bm25_rank"] = rank
            combined_results[document_id]["bm25_score"] = hit["_score"]

            combined_results[document_id]["rrf_score"] += (
                1 / (RANK_CONSTANT + rank)
            )

        for rank, hit in enumerate(
            knn_response["hits"]["hits"],
            start=1,
        ):
            document_id = hit["_id"]

            if document_id not in combined_results:
                combined_results[document_id] = {
                    "source": hit["_source"],
                    "bm25_rank": None,
                    "knn_rank": None,
                    "bm25_score": None,
                    "knn_score": None,
                    "rrf_score": 0.0,
                }

            combined_results[document_id]["knn_rank"] = rank
            combined_results[document_id]["knn_score"] = hit["_score"]

            combined_results[document_id]["rrf_score"] += (
                1 / (RANK_CONSTANT + rank)
            )

        ranked_results = sorted(
            combined_results.values(),
            key=lambda result: result["rrf_score"],
            reverse=True,
        )

        # --------------------------------------------------
        # DISPLAY RESULTS
        # --------------------------------------------------

        print()
        print(f"Query: {QUERY}")
        print(f"BM25 results: {len(bm25_response['hits']['hits'])}")
        print(f"kNN results : {len(knn_response['hits']['hits'])}")
        print()

        print("=" * 70)
        print("RRF RANKED RESULTS")
        print("=" * 70)

        for rank, result in enumerate(
            ranked_results[:TOP_K],
            start=1,
        ):
            source = result["source"]

            print()
            print(f"Final Rank  : {rank}")
            print(f"RRF Score   : {result['rrf_score']:.6f}")
            print(f"BM25 Rank   : {result['bm25_rank']}")
            print(f"kNN Rank    : {result['knn_rank']}")
            print(f"BM25 Score  : {result['bm25_score']}")
            print(f"kNN Score   : {result['knn_score']}")
            print(f"Chunk ID    : {source['chunk_id']}")
            print(f"Page        : {source['page_number']}")
            print(
                f"Content     : "
                f"{source['content'][:300]}"
            )
            print("-" * 70)

        print()
        print("=" * 70)
        print("HYBRID SEARCH COMPLETE")
        print("=" * 70)

    finally:
        await es_client.close()


asyncio.run(test_hybrid())