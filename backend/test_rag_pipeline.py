import asyncio

from app.core.elasticsearch import es_client
from app.services.retrieval_service import RetrievalService
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = (
    "nvidia/llama-nemotron-embed-1b-v2"
)

TEST_QUERY = "What is the main purpose of this document?"

TOP_K = 5


async def main():

    print("=" * 80)
    print("RAG RETRIEVAL PIPELINE TEST")
    print("=" * 80)

    print()
    print("Loading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL_NAME,
        trust_remote_code=True,
    )

    print("Embedding model loaded.")

    print()
    print("Creating retrieval service...")

    retrieval_service = RetrievalService(
        embedding_model=embedding_model
    )

    print("Retrieval service created.")

    print()
    print("Running hybrid search...")
    print(f"Query: {TEST_QUERY}")

    results = await retrieval_service.search(
        query_text=TEST_QUERY,
        top_k=TOP_K,
    )

    print()
    print("=" * 80)
    print("RETRIEVAL RESULTS")
    print("=" * 80)

    print()
    print(f"Results returned: {len(results)}")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print()
        print("-" * 80)
        print(f"RESULT {index}")
        print("-" * 80)

        print(
            f"Document    : {result['filename']}"
        )

        print(
            f"Page        : {result['page_number']}"
        )

        print(
            f"Chunk ID     : {result['chunk_id']}"
        )

        print(
            f"RRF Score   : {result['rrf_score']}"
        )

        print(
            f"BM25 Rank   : {result['bm25_rank']}"
        )

        print(
            f"kNN Rank    : {result['knn_rank']}"
        )

        print(
            f"BM25 Score  : {result['bm25_score']}"
        )

        print(
            f"kNN Score   : {result['knn_score']}"
        )

        content = result["content"]

        print()
        print("Content preview:")
        print(content[:500])

    print()
    print("=" * 80)
    print("RAG RETRIEVAL TEST COMPLETE")
    print("=" * 80)

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())