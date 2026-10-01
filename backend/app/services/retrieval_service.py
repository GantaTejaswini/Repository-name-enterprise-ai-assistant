import time
from typing import Any

from app.core.elasticsearch import es_client


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"

RANK_CONSTANT = 20
DEFAULT_RESULTS = 5


class RetrievalService:

    def __init__(self, embedding_model):

        self.model = embedding_model

    async def search(
        self,
        query_text: str,
        tenant_id: str | None = None,
        top_k: int = DEFAULT_RESULTS,
    ) -> dict[str, Any]:

        total_start = time.perf_counter()

        # -------------------------------------------------
        # 1. Generate query embedding
        # -------------------------------------------------

        embedding_start = time.perf_counter()

        query_embedding = self.model.encode(
            query_text,
            normalize_embeddings=False,
        )

        query_vector = query_embedding.tolist()

        embedding_time = (
            time.perf_counter() - embedding_start
        )

        # -------------------------------------------------
        # 2. Tenant filter
        # -------------------------------------------------

        filters = []

        if tenant_id:

            filters.append(
                {
                    "term": {
                        "tenant_id": tenant_id
                    }
                }
            )

        # -------------------------------------------------
        # 3. BM25 search
        # -------------------------------------------------

        bm25_start = time.perf_counter()

        bm25_query = {
            "bool": {
                "must": [
                    {
                        "match": {
                            "content": query_text
                        }
                    }
                ]
            }
        }

        if filters:

            bm25_query["bool"]["filter"] = filters

        bm25_response = await es_client.search(
            index=INDEX_NAME,
            query=bm25_query,
            size=top_k,
        )

        bm25_time = (
            time.perf_counter() - bm25_start
        )

        # -------------------------------------------------
        # 4. kNN search
        # -------------------------------------------------

        knn_start = time.perf_counter()

        knn_request = {
            "field": "embedding",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": max(
                top_k * 10,
                50,
            ),
        }

        if filters:

            knn_request["filter"] = filters

        knn_response = await es_client.search(
            index=INDEX_NAME,
            knn=knn_request,
        )

        knn_time = (
            time.perf_counter() - knn_start
        )

        # -------------------------------------------------
        # 5. Application-level Reciprocal Rank Fusion
        # -------------------------------------------------

        rrf_start = time.perf_counter()

        combined_results: dict[
            str,
            dict[str, Any],
        ] = {}

        # BM25 results

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

            combined_results[
                document_id
            ]["bm25_rank"] = rank

            combined_results[
                document_id
            ]["bm25_score"] = hit["_score"]

            combined_results[
                document_id
            ]["rrf_score"] += (
                1 / (RANK_CONSTANT + rank)
            )

        # kNN results

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

            combined_results[
                document_id
            ]["knn_rank"] = rank

            combined_results[
                document_id
            ]["knn_score"] = hit["_score"]

            combined_results[
                document_id
            ]["rrf_score"] += (
                1 / (RANK_CONSTANT + rank)
            )

        ranked_results = sorted(
            combined_results.values(),
            key=lambda result: result[
                "rrf_score"
            ],
            reverse=True,
        )

        rrf_time = (
            time.perf_counter() - rrf_start
        )

        # -------------------------------------------------
        # 6. Format final results
        # -------------------------------------------------

        results = []

        for result in ranked_results[:top_k]:

            source = result["source"]

            results.append(
                {
                    "chunk_id": source["chunk_id"],
                    "document_id": source["document_id"],
                    "tenant_id": source["tenant_id"],
                    "filename": source["filename"],
                    "page_number": source["page_number"],
                    "content": source["content"],
                    "rrf_score": result["rrf_score"],
                    "bm25_rank": result["bm25_rank"],
                    "knn_rank": result["knn_rank"],
                    "bm25_score": result["bm25_score"],
                    "knn_score": result["knn_score"],
                }
            )

        total_time = (
            time.perf_counter() - total_start
        )

        # -------------------------------------------------
        # 7. Timing information
        # -------------------------------------------------

        timing = {
            "embedding_seconds": round(
                embedding_time,
                3,
            ),
            "bm25_seconds": round(
                bm25_time,
                3,
            ),
            "knn_seconds": round(
                knn_time,
                3,
            ),
            "rrf_seconds": round(
                rrf_time,
                3,
            ),
            "total_seconds": round(
                total_time,
                3,
            ),
        }

        return {
            "results": results,
            "timing": timing,
        }