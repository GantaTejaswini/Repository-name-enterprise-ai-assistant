from typing import Iterable


def hit_at_k(
    retrieved_chunk_ids: Iterable[str],
    relevant_chunk_ids: Iterable[str],
    k: int,
) -> float:
    retrieved = list(retrieved_chunk_ids)[:k]
    relevant = set(relevant_chunk_ids)

    return 1.0 if any(chunk_id in relevant for chunk_id in retrieved) else 0.0


def recall_at_k(
    retrieved_chunk_ids: Iterable[str],
    relevant_chunk_ids: Iterable[str],
    k: int,
) -> float:
    retrieved = set(list(retrieved_chunk_ids)[:k])
    relevant = set(relevant_chunk_ids)

    if not relevant:
        return 0.0

    return len(retrieved.intersection(relevant)) / len(relevant)


def reciprocal_rank(
    retrieved_chunk_ids: Iterable[str],
    relevant_chunk_ids: Iterable[str],
) -> float:
    relevant = set(relevant_chunk_ids)

    for rank, chunk_id in enumerate(retrieved_chunk_ids, start=1):
        if chunk_id in relevant:
            return 1.0 / rank

    return 0.0


def mean(values: Iterable[float]) -> float:
    values = list(values)

    if not values:
        return 0.0

    return sum(values) / len(values)


def calculate_metrics(
    retrieved_chunk_ids: Iterable[str],
    relevant_chunk_ids: Iterable[str],
    k: int,
) -> dict[str, float]:
    retrieved = list(retrieved_chunk_ids)

    return {
        f"hit@{k}": hit_at_k(
            retrieved,
            relevant_chunk_ids,
            k,
        ),
        f"recall@{k}": recall_at_k(
            retrieved,
            relevant_chunk_ids,
            k,
        ),
        "mrr": reciprocal_rank(
            retrieved,
            relevant_chunk_ids,
        ),
    }