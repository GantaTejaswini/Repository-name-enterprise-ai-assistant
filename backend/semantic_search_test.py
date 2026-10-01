import asyncio

from sentence_transformers import SentenceTransformer

from app.core.elasticsearch import es_client


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"


QUERY_TEXT = (
    "How do AI assistants retrieve information from documents "
    "before generating an answer?"
)


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

    print("Running kNN search...")

    try:
        response = await es_client.search(
            index=INDEX_NAME,
            knn={
                "field": "embedding",
                "query_vector": query_embedding.tolist(),
                "k": 5,
                "num_candidates": 50,
            },
        )

        print()
        print("Search results:")
        print("=" * 80)

        for hit in response["hits"]["hits"]:
            source = hit["_source"]

            print("Score:", hit["_score"])
            print("Document ID:", source["document_id"])
            print("Chunk ID:", source["chunk_id"])
            print("Filename:", source["filename"])
            print("Content:", source["content"])
            print("-" * 80)

    finally:
        await es_client.close()


asyncio.run(main())