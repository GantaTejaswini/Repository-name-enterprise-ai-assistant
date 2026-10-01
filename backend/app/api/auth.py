from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.jwt import create_access_token
from app.core.security import verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.audit_service import AuditService


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)

    user = await repository.get_by_email(
        login_request.email
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    password_valid = verify_password(
        login_request.password,
        user.password_hash,
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        username=user.username,
    )

    await AuditService.log(
        db=db,
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="user_login",
        resource_type="user",
        resource_id=user.id,
        details=f"User '{user.username}' logged in successfully.",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )