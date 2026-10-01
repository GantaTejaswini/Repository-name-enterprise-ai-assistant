from fastapi import APIRouter, Request

from app.services.diagnostics_service import (
    DiagnosticsService,
)


router = APIRouter(
    prefix="/api",
    tags=["Diagnostics"],
)


@router.get("/diagnostics")
async def diagnostics(
    request: Request,
):

    postgres_status = (
        await DiagnosticsService.check_postgresql()
    )

    elasticsearch_status = (
        await DiagnosticsService.check_elasticsearch()
    )

    embedding_status = (
        DiagnosticsService.check_embedding_model(
            getattr(
                request.app.state,
                "embedding_model",
                None,
            )
        )
    )

    llm_status = (
        DiagnosticsService.check_llm_model(
            getattr(
                request.app.state,
                "llm_model",
                None,
            )
        )
    )

    rag_status = (
        DiagnosticsService.check_rag_service(
            getattr(
                request.app.state,
                "rag_service",
                None,
            )
        )
    )

    statuses = [
        postgres_status,
        elasticsearch_status,
        embedding_status,
        llm_status,
        rag_status,
    ]

    overall_status = (
        "healthy"
        if all(
            status in {
                "healthy",
                "ready",
            }
            for status in statuses
        )
        else "unhealthy"
    )

    return {
        "status": overall_status,
        "services": {
            "postgresql": postgres_status,
            "elasticsearch": elasticsearch_status,
            "embedding_model": embedding_status,
            "llm_model": llm_status,
            "rag_service": rag_status,
        },
    }