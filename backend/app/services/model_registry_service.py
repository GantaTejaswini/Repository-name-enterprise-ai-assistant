from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model_registry import ModelRegistry


class ModelRegistryService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
    ) -> list[ModelRegistry]:

        result = await db.execute(
            select(ModelRegistry).order_by(
                ModelRegistry.created_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )

    @staticmethod
    async def register_default_models(
        db: AsyncSession,
    ) -> None:

        result = await db.execute(
            select(ModelRegistry)
        )

        existing_models = list(
            result.scalars().all()
        )

        existing_names = {
            model.name
            for model in existing_models
        }

        models = []

        if "Nemotron Embed 1B" not in existing_names:

            models.append(
                ModelRegistry(
                    id=uuid4(),
                    name="Nemotron Embed 1B",
                    provider="NVIDIA",
                    model_type="embedding",
                    version=(
                        "nvidia/"
                        "llama-nemotron-embed-1b-v2"
                    ),
                    dimensions=2048,
                    status="active",
                    description=(
                        "Local NVIDIA Nemotron embedding "
                        "model used for semantic retrieval."
                    ),
                    is_default=True,
                )
            )

        if (
            "Granite 3.3 8B Instruct"
            not in existing_names
        ):

            models.append(
                ModelRegistry(
                    id=uuid4(),
                    name="Granite 3.3 8B Instruct",
                    provider="IBM",
                    model_type="llm",
                    version=(
                        "ibm-granite/"
                        "granite-3.3-8b-instruct"
                    ),
                    dimensions=None,
                    status="available",
                    description=(
                        "IBM Granite instruction-following "
                        "LLM available as an optional local "
                        "generation provider."
                    ),
                    is_default=False,
                )
            )

        if models:

            db.add_all(models)

            await db.commit()