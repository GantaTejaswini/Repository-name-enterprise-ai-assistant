import asyncio

from app.services.retrieval_service import RetrievalService
from app.core.elasticsearch import es_client


async def main():

    print("=" * 80)
    print("TESTING RETRIEVAL SERVICE")
    print("=" * 80)

    print()
    print("Creating retrieval service...")
    service = RetrievalService()

    query = "What programming languages are listed in the resume?"

    print()
    print("Query:", query)
    print()
    print("Searching...")

    results = await service.search(
        query_text=query,
        tenant_id="tenant-demo",
        top_k=5,
    )

    print()
    print("=" * 80)
    print("RETRIEVAL RESULTS")
    print("=" * 80)

    for rank, result in enumerate(results, start=1):

        print()
        print(f"Result {rank}")
        print("-" * 80)

        print("RRF Score:", result["rrf_score"])
        print("BM25 Rank:", result["bm25_rank"])
        print("kNN Rank:", result["knn_rank"])
        print("BM25 Score:", result["bm25_score"])
        print("kNN Score:", result["knn_score"])
        print("Page:", result["page_number"])
        print("Chunk ID:", result["chunk_id"])

        print()
        print("Content:")
        print(result["content"])

    await es_client.close()

    print()
    print("=" * 80)
    print("RETRIEVAL TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())