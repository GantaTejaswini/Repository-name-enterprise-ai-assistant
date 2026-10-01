from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db


router = APIRouter(
    prefix="/api",
    tags=["Database"],
)


@router.get("/database-test")
async def database_test(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        text("SELECT 1")
    )

    value = result.scalar_one()

    return {
        "database": "connected",
        "test_result": value,
    }