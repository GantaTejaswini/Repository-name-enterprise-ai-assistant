import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole


TENANT_NAME = "Demo Company"
USERNAME = "demo"
EMAIL = "demo@company.com"
PASSWORD = "password123"
ROLE_NAME = "admin"


async def create_demo_account():
    async with AsyncSessionLocal() as db:

        # --------------------------------------------------
        # TENANT
        # --------------------------------------------------

        result = await db.execute(
            select(Tenant).where(
                Tenant.name == TENANT_NAME
            )
        )

        tenant = result.scalar_one_or_none()

        if tenant is None:
            tenant = Tenant(
                name=TENANT_NAME
            )

            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)

            print("Demo tenant created.")

        else:
            print("Demo tenant already exists.")

        # --------------------------------------------------
        # USER
        # --------------------------------------------------

        result = await db.execute(
            select(User).where(
                User.email == EMAIL
            )
        )

        user = result.scalar_one_or_none()

        if user is None:

            user = User(
                tenant_id=tenant.id,
                username=USERNAME,
                email=EMAIL,
                password_hash=hash_password(PASSWORD),
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

            print("Demo user created.")

        else:

            user.tenant_id = tenant.id
            user.username = USERNAME
            user.password_hash = hash_password(PASSWORD)

            await db.commit()
            await db.refresh(user)

            print("Demo user already existed.")
            print("Password has been reset.")

        # --------------------------------------------------
        # ADMIN ROLE
        # --------------------------------------------------

        result = await db.execute(
            select(Role).where(
                Role.tenant_id == tenant.id,
                Role.name == ROLE_NAME,
            )
        )

        role = result.scalar_one_or_none()

        if role is None:

            role = Role(
                tenant_id=tenant.id,
                name=ROLE_NAME,
            )

            db.add(role)
            await db.commit()
            await db.refresh(role)

            print("Admin role created.")

        else:
            print("Admin role already exists.")

        # --------------------------------------------------
        # ASSIGN ROLE
        # --------------------------------------------------

        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
            )
        )

        user_role = result.scalar_one_or_none()

        if user_role is None:

            user_role = UserRole(
                user_id=user.id,
                role_id=role.id,
            )

            db.add(user_role)
            await db.commit()

            print("Admin role assigned.")

        else:
            print("Admin role already assigned.")

        print()
        print("=" * 60)
        print("DEMO ACCOUNT READY")
        print("=" * 60)
        print(f"Company  : {TENANT_NAME}")
        print(f"Username : {USERNAME}")
        print(f"Email    : {EMAIL}")
        print(f"Password : {PASSWORD}")
        print(f"Role     : {ROLE_NAME}")
        print(f"Tenant ID: {tenant.id}")
        print("=" * 60)


asyncio.run(create_demo_account())