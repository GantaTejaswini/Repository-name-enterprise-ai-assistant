from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class Source(BaseModel):
    document: str
    page: int
    chunk_id: str
    rrf_score: float
    content: str


class RetrievalTiming(BaseModel):
    embedding_seconds: float
    bm25_seconds: float
    knn_seconds: float
    rrf_seconds: float
    total_seconds: float


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]

    retrieval_timing: RetrievalTiming
    generation_seconds: float
    llm_provider: str