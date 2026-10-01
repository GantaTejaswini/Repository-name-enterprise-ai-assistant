import asyncio

from app.core.elasticsearch import es_client


async def main():
    mapping = await es_client.indices.get_mapping(
        index="document_chunks"
    )

    print(mapping)

    await es_client.close()


asyncio.run(main())