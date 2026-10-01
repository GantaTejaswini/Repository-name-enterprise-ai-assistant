from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.dependencies import get_db
from app.core.rbac import require_admin
from app.services.model_registry_service import ModelRegistryService


router = APIRouter(
    prefix="/api/models",
    tags=["Model Registry"],
)


@router.get("")
async def get_models(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    models = await ModelRegistryService.get_all(
        db=db,
    )

    return {
        "models": [
            {
                "id": str(model.id),
                "name": model.name,
                "provider": model.provider,
                "model_type": model.model_type,
                "version": model.version,
                "dimensions": model.dimensions,
                "status": model.status,
                "description": model.description,
                "is_default": model.is_default,
                "created_at": model.created_at.isoformat(),
            }
            for model in models
        ]
    }


@router.post("/seed")
async def seed_models(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    await ModelRegistryService.register_default_models(
        db=db,
    )

    models = await ModelRegistryService.get_all(
        db=db,
    )

    return {
        "message": "Default models registered successfully.",
        "count": len(models),
    }