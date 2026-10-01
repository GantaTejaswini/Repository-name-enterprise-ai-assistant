import asyncio

from app.core.database import Base, engine
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.audit_log import AuditLog


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")

    await engine.dispose()


asyncio.run(create_tables())