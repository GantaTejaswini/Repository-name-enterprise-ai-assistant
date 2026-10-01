from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.dependencies import get_db
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.services.audit_service import AuditService


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    current_user: dict = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
):

    rag_service = getattr(
        request.app.state,
        "rag_service",
        None,
    )

    if rag_service is None:

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail="RAG service is not ready",
        )

    try:

        result = await rag_service.ask(
            question=chat_request.question,
            tenant_id=current_user["tenant_id"],
            top_k=chat_request.top_k,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Failed to process the RAG request",
        ) from exc

    await AuditService.log(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        action="rag_chat",
        resource_type="chat",
        details=(
            "RAG question processed successfully. "
            f"Question='{chat_request.question}', "
            f"Sources={len(result['sources'])}"
        ),
    )

    return result