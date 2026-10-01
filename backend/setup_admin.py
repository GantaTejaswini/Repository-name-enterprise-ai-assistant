import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole


TENANT_ID = "9984bc36-f841-44bd-899a-2a62c755f5ec"

USER_ID = "186c10a6-42d3-465b-afaf-b85887cd13e0"


async def setup_admin():

    async with AsyncSessionLocal() as db:

        tenant_result = await db.execute(
            select(Tenant).where(
                Tenant.id == TENANT_ID
            )
        )

        tenant = tenant_result.scalar_one_or_none()

        if tenant is None:

            print("Tenant not found.")
            return

        user_result = await db.execute(
            select(User).where(
                User.id == USER_ID,
                User.tenant_id == TENANT_ID,
            )
        )

        user = user_result.scalar_one_or_none()

        if user is None:

            print("Admin user not found.")
            return

        role_result = await db.execute(
            select(Role).where(
                Role.tenant_id == TENANT_ID,
                Role.name == "admin",
            )
        )

        role = role_result.scalar_one_or_none()

        if role is None:

            role = Role(
                tenant_id=TENANT_ID,
                name="admin",
            )

            db.add(role)

            await db.flush()

            print("Admin role created.")

        else:

            print("Admin role already exists.")

        assignment_result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == USER_ID,
                UserRole.role_id == role.id,
            )
        )

        assignment = assignment_result.scalar_one_or_none()

        if assignment is None:

            assignment = UserRole(
                user_id=USER_ID,
                role_id=role.id,
            )

            db.add(assignment)

            print("Admin role assigned to user.")

        else:

            print("Admin role already assigned.")

        await db.commit()

        print()
        print("Admin setup completed successfully!")
        print(f"Tenant: {tenant.name}")
        print(f"User: {user.username}")
        print(f"Role: {role.name}")
        print(f"Role ID: {role.id}")


asyncio.run(setup_admin())