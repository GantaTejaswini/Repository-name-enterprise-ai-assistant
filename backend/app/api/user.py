from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.rbac import require_role
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserResponse


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.post(
    "/",
    response_model=UserResponse,
)
async def create_user(
    user_request: UserCreateRequest,
    current_user: dict = Depends(
        require_role("admin")
    ),
    db: AsyncSession = Depends(get_db),
):

    repository = UserRepository(db)

    user = await repository.create(
        tenant_id=current_user["tenant_id"],
        username=user_request.username,
        email=user_request.email,
        password=user_request.password,
    )

    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        username=user.username,
        email=user.email,
        created_at=user.created_at.isoformat(),
    )