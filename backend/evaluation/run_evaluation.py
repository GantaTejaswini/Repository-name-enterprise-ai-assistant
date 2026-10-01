import asyncio
import json
import time

from sentence_transformers import SentenceTransformer

from app.services.retrieval_service import RetrievalService
from evaluation.dataset import EVALUATION_CASES, TENANT_A_ID
from evaluation.metrics import calculate_metrics, mean

MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"
TOP_K = 5


async def run_evaluation() -> None:
    print("=" * 70)
    print("ENTERPRISE AI ASSISTANT - RAG RETRIEVAL EVALUATION")
    print("=" * 70)
    print()

    print(f"Loading embedding model: {MODEL_NAME}")
    model_start = time.perf_counter()

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    model_load_time = time.perf_counter() - model_start
    print(f"Embedding model loaded in {model_load_time:.2f} seconds")
    print()

    retrieval_service = RetrievalService(model)

    case_results = []
    hit_scores = []
    recall_scores = []
    mrr_scores = []

    for index, case in enumerate(EVALUATION_CASES, start=1):
        print("-" * 70)
        print(f"CASE {index}/{len(EVALUATION_CASES)}")
        print(f"Question: {case.question}")

        result = await retrieval_service.search(
            query_text=case.question,
            tenant_id=TENANT_A_ID,
            top_k=TOP_K,
        )

        retrieved_ids = [
            item["chunk_id"]
            for item in result["results"]
        ]

        metrics = calculate_metrics(
            retrieved_chunk_ids=retrieved_ids,
            relevant_chunk_ids=case.relevant_chunk_ids,
            k=TOP_K,
        )

        hit_scores.append(metrics[f"hit@{TOP_K}"])
        recall_scores.append(metrics[f"recall@{TOP_K}"])
        mrr_scores.append(metrics["mrr"])

        first_relevant_rank = None
        relevant_ids = set(case.relevant_chunk_ids)

        for rank, chunk_id in enumerate(
            retrieved_ids,
            start=1,
        ):
            if chunk_id in relevant_ids:
                first_relevant_rank = rank
                break

        print()
        print("Expected relevant chunks:")
        for chunk_id in case.relevant_chunk_ids:
            print(f"  - {chunk_id}")

        print()
        print("Retrieved chunks:")
        for rank, item in enumerate(
            result["results"],
            start=1,
        ):
            relevant_marker = (
                "RELEVANT"
                if item["chunk_id"] in relevant_ids
                else "not relevant"
            )

            print(
                f"  {rank}. "
                f"{item['chunk_id']} "
                f"[{relevant_marker}]"
            )

        print()
        print(f"Hit@{TOP_K}: {metrics[f'hit@{TOP_K}']:.3f}")
        print(f"Recall@{TOP_K}: {metrics[f'recall@{TOP_K}']:.3f}")
        print(f"MRR: {metrics['mrr']:.3f}")

        if first_relevant_rank is None:
            print("First relevant rank: NOT FOUND")
        else:
            print(
                f"First relevant rank: "
                f"{first_relevant_rank}"
            )

        print(
            "Retrieval timing: "
            f"{result['timing']['total_seconds']:.3f}s"
        )

        case_results.append(
            {
                "question": case.question,
                "expected_relevant_chunks": list(
                    case.relevant_chunk_ids
                ),
                "retrieved_chunks": retrieved_ids,
                "metrics": metrics,
                "timing": result["timing"],
                "first_relevant_rank": first_relevant_rank,
            }
        )

    summary = {
        "evaluation_cases": len(EVALUATION_CASES),
        "top_k": TOP_K,
        f"mean_hit@{TOP_K}": mean(hit_scores),
        f"mean_recall@{TOP_K}": mean(recall_scores),
        "mean_mrr": mean(mrr_scores),
        "model": MODEL_NAME,
        "tenant_id": TENANT_A_ID,
        "cases": case_results,
    }

    print()
    print("=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Cases: {summary['evaluation_cases']}")
    print(
        f"Hit@{TOP_K}: "
        f"{summary[f'mean_hit@{TOP_K}']:.3f}"
    )
    print(
        f"Recall@{TOP_K}: "
        f"{summary[f'mean_recall@{TOP_K}']:.3f}"
    )
    print(
        f"MRR: "
        f"{summary['mean_mrr']:.3f}"
    )
    print("=" * 70)

    output_path = "evaluation/results.json"

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
    asyncio.run(run_evaluation())