from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user_role import UserRole


class RoleRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        tenant_id: str,
        name: str,
    ) -> Role:

        role = Role(
            tenant_id=tenant_id,
            name=name,
        )

        self.db.add(role)

        await self.db.commit()

        await self.db.refresh(role)

        return role

    async def get_by_name(
        self,
        tenant_id: str,
        name: str,
    ) -> Role | None:

        result = await self.db.execute(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.name == name,
            )
        )

        return result.scalar_one_or_none()

    async def assign_role(
        self,
        user_id: str,
        role_id: str,
    ) -> UserRole:

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        self.db.add(user_role)

        await self.db.commit()

        await self.db.refresh(user_role)

        return user_role

    async def user_has_role(
        self,
        user_id: str,
        tenant_id: str,
        role_name: str,
    ) -> bool:

        result = await self.db.execute(
            select(UserRole)
            .join(
                Role,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_id == user_id,
                Role.tenant_id == tenant_id,
                Role.name == role_name,
            )
        )

        return result.scalar_one_or_none() is not None