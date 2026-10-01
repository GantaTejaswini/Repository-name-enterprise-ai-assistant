import asyncio

from sentence_transformers import SentenceTransformer

from app.core.elasticsearch import es_client


MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
INDEX_NAME = "document_chunks"


TEXT = (
    "Enterprise AI assistants use retrieval augmented generation "
    "to retrieve relevant information from documents before "
    "generating an answer with a large language model."
)


async def main():

    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    print("Model loaded successfully!")

    print("Generating embedding...")

    embedding = model.encode(
        TEXT,
        normalize_embeddings=False,
    )

    print("Embedding shape:", embedding.shape)

    embedding_list = embedding.tolist()

    document = {
        "document_id": "test-document-002",
        "tenant_id": "tenant-demo",
        "filename": "enterprise_ai_guide.pdf",
        "page_number": 1,
        "chunk_id": "chunk-real-001",
        "content": TEXT,
        "embedding": embedding_list,
        "metadata": {
            "source": "test",
            "document_type": "pdf",
        },
    }

    print("Indexing document into Elasticsearch...")

    try:
        response = await es_client.index(
            index=INDEX_NAME,
            id=document["chunk_id"],
            document=document,
        )

        await es_client.indices.refresh(index=INDEX_NAME)

        print("Document indexed:", response["result"])

    finally:
        await es_client.close()


asyncio.run(main())