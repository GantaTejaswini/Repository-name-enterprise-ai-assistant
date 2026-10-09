from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    model_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    dimensions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
