from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.services.retrieval_service import RetrievalService


router = APIRouter(
    prefix="/api",
    tags=["Retrieval"],
)


class RetrievalRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=4000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


@router.post("/retrieval")
async def retrieval(
    retrieval_request: RetrievalRequest,
    request: Request,
    current_user: dict = Depends(
        get_current_user
    ),
):

    embedding_model = getattr(
        request.app.state,
        "embedding_model",
        None,
    )

    if embedding_model is None:

        return {
            "status": "not_ready",
            "message": (
                "Embedding model is not ready."
            ),
        }

    retrieval_service = RetrievalService(
        embedding_model
    )

    retrieval_response = (
        await retrieval_service.search(
            query_text=retrieval_request.question,
            tenant_id=current_user["tenant_id"],
            top_k=retrieval_request.top_k,
        )
    )

    return {
        "question": retrieval_request.question,
        "tenant_id": current_user["tenant_id"],
        "top_k": retrieval_request.top_k,
        "results": retrieval_response["results"],
        "timing": retrieval_response["timing"],
    }