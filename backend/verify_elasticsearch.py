import asyncio

from app.core.elasticsearch import es_client


INDEX_NAME = "document_chunks"


async def main():

    print("=" * 80)
    print("ELASTICSEARCH INGESTION VERIFICATION")
    print("=" * 80)

    count_response = await es_client.count(
        index=INDEX_NAME,
    )

    count = count_response["count"]

    print()
    print(f"Elasticsearch document count: {count}")

    search_response = await es_client.search(
        index=INDEX_NAME,
        size=1,
        query={
            "term": {
                "document_id": (
                    "1bbbc11d-b4d5-4b1a-8529-19ddf4fde999"
                )
            }
        },
    )

    matching_count = search_response["hits"]["total"]

    if isinstance(matching_count, dict):
        matching_count = matching_count["value"]

    print(
        "Chunks for uploaded document:"
        f" {matching_count}"
    )

    print()

    if matching_count == 1074:
        print(
            "SUCCESS: All 1074 document chunks "
            "are present in Elasticsearch."
        )
    else:
        print(
            "WARNING: Expected 1074 chunks but "
            f"found {matching_count}."
        )

    print()
    print("=" * 80)
    print("ELASTICSEARCH VERIFICATION COMPLETE")
    print("=" * 80)

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())