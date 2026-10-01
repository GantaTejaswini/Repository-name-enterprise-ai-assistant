from datetime import datetime

from pydantic import BaseModel, Field


class TenantCreateRequest(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=255,
    )


class TenantResponse(BaseModel):

    id: str
    name: str
    created_at: datetime