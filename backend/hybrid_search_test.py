import asyncio

from sentence_transformers import SentenceTransformer

from app.core.elasticsearch import es_client


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"

QUERY_TEXT = (
    "How do AI assistants retrieve information from documents "
    "before generating an answer?"
)

RANK_CONSTANT = 20


async def main():

    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    print("Model loaded successfully!")

    print("Generating query embedding...")

    query_embedding = model.encode(
        QUERY_TEXT,
        normalize_embeddings=False,
    )

    print("Query embedding shape:", query_embedding.shape)

    try:

        # --------------------------------------------------
        # 1. BM25 SEARCH
        # --------------------------------------------------

        print()
        print("Running BM25 search...")

        bm25_response = await es_client.search(
            index=INDEX_NAME,
            query={
                "match": {
                    "content": QUERY_TEXT
                }
            },
            size=10,
        )

        # --------------------------------------------------
        # 2. KNN SEARCH
        # --------------------------------------------------

        print("Running kNN search...")

        knn_response = await es_client.search(
            index=INDEX_NAME,
            knn={
                "field": "embedding",
                "query_vector": query_embedding.tolist(),
                "k": 10,
                "num_candidates": 50,
            },
        )

        # --------------------------------------------------
        # 3. BUILD RRF SCORES
        # --------------------------------------------------

        combined_results = {}

        # BM25 ranking
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
                    "rrf_score": 0.0,
                }

            combined_results[document_id]["bm25_rank"] = rank

            combined_results[document_id]["rrf_score"] += (
                1 / (RANK_CONSTANT + rank)
            )

        # kNN ranking
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
                    "rrf_score": 0.0,
                }

            combined_results[document_id]["knn_rank"] = rank

            combined_results[document_id]["rrf_score"] += (
                1 / (RANK_CONSTANT + rank)
            )

        # --------------------------------------------------
        # 4. SORT BY COMBINED RRF SCORE
        # --------------------------------------------------

        ranked_results = sorted(
            combined_results.values(),
            key=lambda result: result["rrf_score"],
            reverse=True,
        )

        # --------------------------------------------------
        # 5. DISPLAY RESULTS
        # --------------------------------------------------

        print()
        print("Hybrid Search Results")
        print("=" * 80)

        for result in ranked_results:

            source = result["source"]

            print("RRF Score:", result["rrf_score"])
            print("BM25 Rank:", result["bm25_rank"])
            print("kNN Rank:", result["knn_rank"])
            print("Document ID:", source["document_id"])
            print("Chunk ID:", source["chunk_id"])
            print("Filename:", source["filename"])
            print("Content:", source["content"])

            print("-" * 80)

    finally:
        await es_client.close()


asyncio.run(main())