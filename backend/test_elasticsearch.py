import asyncio
from app.core.elasticsearch import es_client


async def main():
    info = await es_client.info()

    print("Elasticsearch:", info["version"]["number"])
    print("Cluster:", info["cluster_name"])

    await es_client.close()


asyncio.run(main())