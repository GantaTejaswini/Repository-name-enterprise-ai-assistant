from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.rbac import require_role
from app.repositories.tenant_repository import TenantRepository
from app.schemas.tenant import (
    TenantCreateRequest,
    TenantResponse,
)
from app.services.audit_service import AuditService


router = APIRouter(
    prefix="/api/tenants",
    tags=["Tenants"],
)


@router.post(
    "/",
    response_model=TenantResponse,
)
async def create_tenant(
    tenant_request: TenantCreateRequest,
    current_user: dict = Depends(
        require_role("admin")
    ),
    db: AsyncSession = Depends(get_db),
):

    repository = TenantRepository(db)

    existing_tenant = await repository.get_by_name(
        tenant_request.name
    )

    if existing_tenant is not None:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant with this name already exists",
        )

    tenant = await repository.create(
        name=tenant_request.name
    )

    await AuditService.log(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
        action="tenant_created",
        resource_type="tenant",
        resource_id=tenant.id,
        details=(
            f"Tenant '{tenant.name}' "
            f"created by user "
            f"'{current_user['username']}'."
        ),
    )

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        created_at=tenant.created_at,
    )