from elasticsearch import AsyncElasticsearch

from app.core.config import settings


es_client = AsyncElasticsearch(
    settings.elasticsearch_url
)
