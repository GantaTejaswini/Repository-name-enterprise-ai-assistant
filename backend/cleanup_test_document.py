import asyncio

from app.core.elasticsearch import es_client


INDEX_NAME = "document_chunks"
DOCUMENT_ID = "chunk-001"


async def main():

    try:
        response = await es_client.delete(
            index=INDEX_NAME,
            id=DOCUMENT_ID,
        )

        print("Delete result:", response["result"])

        await es_client.indices.refresh(index=INDEX_NAME)

    except Exception as e:
        print("Error:", e)

    finally:
        await es_client.close()


asyncio.run(main())