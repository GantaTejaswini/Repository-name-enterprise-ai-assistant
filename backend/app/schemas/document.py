from pydantic import BaseModel


class DocumentResponse(BaseModel):

    id: str
    tenant_id: str
    filename: str
    status: str
    created_at: str


class DocumentListResponse(BaseModel):

    documents: list[DocumentResponse]
    total: int