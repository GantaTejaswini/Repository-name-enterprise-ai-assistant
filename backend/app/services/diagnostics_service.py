from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.elasticsearch import es_client


class DiagnosticsService:

    @staticmethod
    async def check_postgresql() -> str:

        try:
            async with engine.connect() as connection:
                await connection.execute(
                    text("SELECT 1")
                )

            return "healthy"

        except Exception:
            return "unhealthy"

    @staticmethod
    async def check_elasticsearch() -> str:

        try:
            await es_client.info()

            return "healthy"

        except Exception:
            return "unhealthy"

    @staticmethod
    def check_embedding_model(
        embedding_model,
    ) -> str:

        if embedding_model is None:
            return "not_ready"

        return "ready"

    @staticmethod
    def check_llm_model(
        llm_model,
    ) -> str:

        provider = (
            settings.llm_provider
            .lower()
            .strip()
        )

        if provider == "extractive":
            return "ready"

        if provider == "granite":

            if llm_model is None:
                return "not_ready"

            return "ready"

        return "not_ready"

    @staticmethod
    def check_rag_service(
        rag_service,
    ) -> str:

        if rag_service is None:
            return "not_ready"

        return "ready"