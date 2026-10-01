from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant


class TenantRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        name: str,
    ) -> Tenant:

        tenant = Tenant(
            name=name,
        )

        self.db.add(tenant)

        await self.db.commit()

        await self.db.refresh(
            tenant
        )

        return tenant

    async def get_by_id(
        self,
        tenant_id: str,
    ) -> Tenant | None:

        result = await self.db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Tenant | None:

        result = await self.db.execute(
            select(Tenant).where(
                Tenant.name == name
            )
        )

        return result.scalar_one_or_none()