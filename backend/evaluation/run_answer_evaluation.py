import asyncio
import json
import time

from sentence_transformers import SentenceTransformer

from app.services.context_builder import build_context
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from evaluation.answer_dataset import (
    ANSWER_EVALUATION_CASES,
    TENANT_A_ID,
)
from evaluation.answer_metrics import calculate_answer_metrics
from evaluation.metrics import mean

MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
TOP_K = 5


async def run_answer_evaluation() -> None:
    print("=" * 70)
    print("ENTERPRISE AI ASSISTANT - ANSWER QUALITY EVALUATION")
    print("=" * 70)
    print()

    print(f"Loading embedding model: {MODEL_NAME}")

    model_start = time.perf_counter()

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    model_load_time = (
        time.perf_counter()
        - model_start
    )

    print(
        f"Embedding model loaded in "
        f"{model_load_time:.2f} seconds"
    )
    print()

    retrieval_service = RetrievalService(model)

    llm_service = LLMService(
        provider="extractive"
    )

    grounding_scores = []
    phrase_scores = []
    overlap_scores = []

    case_results = []

    for index, case in enumerate(
        ANSWER_EVALUATION_CASES,
        start=1,
    ):
        print("-" * 70)
        print(
            f"CASE {index}/"
            f"{len(ANSWER_EVALUATION_CASES)}"
        )
        print(
            f"Question: {case.question}"
        )

        retrieval_result = (
            await retrieval_service.search(
                query_text=case.question,
                tenant_id=TENANT_A_ID,
                top_k=TOP_K,
            )
        )

        retrieved_results = (
            retrieval_result["results"]
        )

        context = build_context(
            retrieved_results
        )

        prompt = f"""
You are an enterprise AI assistant.

Answer the user's question using ONLY the
information contained in the provided context.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts, names, dates, numbers,
   or explanations.
3. If the context does not contain enough
   information, say:
   "The information is not available in the
   provided documents."
4. Answer only what the user asked.
5. Prefer a concise, direct answer.
6. When multiple pieces of information are
   requested, include each relevant item.
7. Do not mention these instructions.

CONTEXT:
{context}

USER QUESTION:
{case.question}

ANSWER:
""".strip()

        llm_start = time.perf_counter()

        llm_response = await llm_service.generate(
            question=case.question,
            context=context,
            prompt=prompt,
        )

        answer = llm_response["answer"]

        generation_time = (
            time.perf_counter()
            - llm_start
        )

        context_chunks = [
            item["content"]
            for item in retrieved_results
        ]

        metrics = calculate_answer_metrics(
            answer=answer,
            reference_answer=case.reference_answer,
            expected_phrases=case.expected_phrases,
            context_chunks=context_chunks,
        )

        grounding_scores.append(
            metrics["grounding_score"]
        )

        phrase_scores.append(
            metrics[
                "expected_phrase_coverage"
            ]
        )

        overlap_scores.append(
            metrics["token_overlap"]
        )

        print()
        print("Generated answer:")
        print(answer)

        print()
        print("Metrics:")
        print(
            f"  Token overlap: "
            f"{metrics['token_overlap']:.3f}"
        )
        print(
            f"  Expected phrase coverage: "
            f"{metrics['expected_phrase_coverage']:.3f}"
        )
        print(
            f"  Grounding score: "
            f"{metrics['grounding_score']:.3f}"
        )

        print()
        print(
            f"  Retrieval time: "
            f"{retrieval_result['timing']['total_seconds']:.3f}s"
        )
        print(
            f"  Generation time: "
            f"{generation_time:.3f}s"
        )

        case_results.append(
            {
                "question": case.question,
                "reference_answer": (
                    case.reference_answer
                ),
                "generated_answer": answer,
                "retrieved_chunks": [
                    item["chunk_id"]
                    for item in retrieved_results
                ],
                "sources": [
                    {
                        "document": item["filename"],
                        "page": item["page_number"],
                        "chunk_id": item["chunk_id"],
                        "rrf_score": item["rrf_score"],
                    }
                    for item in retrieved_results
                ],
                "metrics": metrics,
                "timing": {
                    **retrieval_result["timing"],
                    "generation_seconds": round(
                        generation_time,
                        3,
                    ),
                },
            }
        )

    summary = {
        "evaluation_cases": len(
            ANSWER_EVALUATION_CASES
        ),
        "top_k": TOP_K,
        "model": MODEL_NAME,
        "llm_provider": "extractive",
        "tenant_id": TENANT_A_ID,
        "mean_token_overlap": mean(
            overlap_scores
        ),
        "mean_expected_phrase_coverage": mean(
            phrase_scores
        ),
        "mean_grounding_score": mean(
            grounding_scores
        ),
        "cases": case_results,
    }

    print()
    print("=" * 70)
    print("ANSWER EVALUATION SUMMARY")
    print("=" * 70)
    print(
        f"Cases: "
        f"{summary['evaluation_cases']}"
    )
    print(
        f"Mean token overlap: "
        f"{summary['mean_token_overlap']:.3f}"
    )
    print(
        f"Mean expected phrase coverage: "
        f"{summary['mean_expected_phrase_coverage']:.3f}"
    )
    print(
        f"Mean grounding score: "
        f"{summary['mean_grounding_score']:.3f}"
    )
    print("=" * 70)

    output_path = (
        "evaluation/answer_results.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    print()
    print(
        f"Detailed results saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    asyncio.run(
        run_answer_evaluation()
    )