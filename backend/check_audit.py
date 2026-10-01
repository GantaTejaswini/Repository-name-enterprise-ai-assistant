import asyncio

from sqlalchemy import text

from app.core.database import engine


async def check_audit():
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT action, resource_type, resource_id, "
                "user_id, tenant_id, details, created_at "
                "FROM audit_logs "
                "ORDER BY created_at DESC "
                "LIMIT 10"
            )
        )

        for row in result:
            print(row)

    await engine.dispose()


asyncio.run(check_audit())