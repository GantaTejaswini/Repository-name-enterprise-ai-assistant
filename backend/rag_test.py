import asyncio

from app.services.rag_service import RAGService


async def main():

    print("=" * 80)
    print("END-TO-END RAG TEST")
    print("=" * 80)

    print()
    print("Creating RAG service...")
    rag_service = RAGService()

    question = "What programming languages are listed in the resume?"

    print()
    print("Question:")
    print(question)

    print()
    print("Generating RAG answer...")
    print("This may take some time because Granite is running on CPU.")

    result = await rag_service.ask(
        question=question,
        tenant_id="tenant-demo",
        top_k=5,
    )

    print()
    print("=" * 80)
    print("RAG ANSWER")
    print("=" * 80)

    print()
    print(result["answer"])

    print()
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for index, source in enumerate(result["sources"], start=1):

        print()
        print(f"Source {index}")
        print("-" * 80)
        print("Document:", source["document"])
        print("Page:", source["page"])
        print("Chunk ID:", source["chunk_id"])
        print("RRF Score:", source["rrf_score"])

    print()
    print("=" * 80)
    print("END-TO-END RAG TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())