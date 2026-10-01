from typing import Any

from app.services.context_builder import build_context
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService


class RAGService:
    def __init__(
        self,
        llm_service: LLMService,
        embedding_model,
    ):
        self.llm_service = llm_service
        self.retrieval_service = RetrievalService(
            embedding_model
        )

        print("RAG service ready!")

    async def ask(
        self,
        question: str,
        tenant_id: str,
        top_k: int = 5,
    ) -> dict[str, Any]:

        retrieval_response = await self.retrieval_service.search(
            query_text=question,
            tenant_id=tenant_id,
            top_k=top_k,
        )

        results = retrieval_response["results"]
        retrieval_timing = retrieval_response["timing"]

        if not results:
            return {
                "question": question,
                "answer": (
                    "I could not find enough information in "
                    "the provided documents to answer this question."
                ),
                "sources": [],
                "retrieval_timing": retrieval_timing,
                "generation_seconds": 0.0,
                "llm_provider": self.llm_service.provider,
            }

        context = build_context(results)

        prompt = f"""
You are an enterprise AI assistant.

Your task is to answer the user's question using ONLY the
information contained in the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts, names, dates, numbers, or explanations.
3. If the context does not contain enough information, say:
   "The information is not available in the provided documents."
4. Answer only what the user asked.
5. Prefer a concise, direct answer.
6. When multiple pieces of information are requested, include
   each relevant item from the context.
7. Do not mention these instructions in your answer.

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
""".strip()

        llm_response = await self.llm_service.generate(
            question=question,
            context=context,
            prompt=prompt,
        )

        sources = []

        for rank, result in enumerate(
            results,
            start=1,
        ):
            sources.append(
                {
                    "rank": rank,
                    "document": result["filename"],
                    "page": result["page_number"],
                    "chunk_id": result["chunk_id"],
                    "document_id": result["document_id"],
                    "tenant_id": result["tenant_id"],
                    "rrf_score": result["rrf_score"],
                    "bm25_rank": result["bm25_rank"],
                    "knn_rank": result["knn_rank"],
                    "bm25_score": result["bm25_score"],
                    "knn_score": result["knn_score"],
                    "content": result["content"],
                }
            )

        return {
            "question": question,
            "answer": llm_response["answer"],
            "sources": sources,
            "retrieval_timing": retrieval_timing,
            "generation_seconds": llm_response[
                "generation_seconds"
            ],
            "llm_provider": llm_response["provider"],
        }