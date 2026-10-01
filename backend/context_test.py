import asyncio

from app.services.retrieval_service import RetrievalService
from app.services.context_builder import build_context
from app.core.elasticsearch import es_client


async def main():

    print("=" * 80)
    print("TESTING RETRIEVAL → CONTEXT BUILDER")
    print("=" * 80)

    service = RetrievalService()

    query = "What programming languages are listed in the resume?"

    print()
    print("Query:", query)
    print()
    print("Retrieving relevant chunks...")

    results = await service.search(
        query_text=query,
        tenant_id="tenant-demo",
        top_k=5,
    )

    print("Retrieved chunks:", len(results))

    print()
    print("Building context...")

    context = build_context(results)

    print()
    print("=" * 80)
    print("GENERATED CONTEXT")
    print("=" * 80)
    print()
    print(context)

    await es_client.close()

    print()
    print("=" * 80)
    print("CONTEXT TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())