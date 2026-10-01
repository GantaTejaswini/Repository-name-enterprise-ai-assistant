from typing import Iterable


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def token_set(text: str) -> set[str]:
    normalized = normalize_text(text)
    return {
        token.strip(".,!?;:()[]{}\"'")
        for token in normalized.split()
        if token.strip(".,!?;:()[]{}\"'")
    }


def token_overlap(
    answer: str,
    reference: str,
) -> float:
    answer_tokens = token_set(answer)
    reference_tokens = token_set(reference)

    if not reference_tokens:
        return 0.0

    overlap = answer_tokens.intersection(reference_tokens)

    return len(overlap) / len(reference_tokens)


def exact_match(
    answer: str,
    reference: str,
) -> float:
    return 1.0 if normalize_text(answer) == normalize_text(reference) else 0.0


def contains_expected_phrases(
    answer: str,
    expected_phrases: Iterable[str],
) -> float:
    normalized_answer = normalize_text(answer)

    phrases = [
        normalize_text(phrase)
        for phrase in expected_phrases
    ]

    if not phrases:
        return 0.0

    matched = sum(
        1
        for phrase in phrases
        if phrase in normalized_answer
    )

    return matched / len(phrases)


def grounding_score(
    answer: str,
    context_chunks: Iterable[str],
) -> float:
    context = normalize_text(
        " ".join(context_chunks)
    )

    answer_tokens = token_set(answer)

    if not answer_tokens:
        return 0.0

    grounded_tokens = {
        token
        for token in answer_tokens
        if token in context
    }

    return len(grounded_tokens) / len(answer_tokens)


def calculate_answer_metrics(
    answer: str,
    reference_answer: str,
    expected_phrases: Iterable[str],
    context_chunks: Iterable[str],
) -> dict[str, float]:
    return {
        "exact_match": exact_match(
            answer,
            reference_answer,
        ),
        "token_overlap": token_overlap(
            answer,
            reference_answer,
        ),
        "expected_phrase_coverage": contains_expected_phrases(
            answer,
            expected_phrases,
        ),
        "grounding_score": grounding_score(
            answer,
            context_chunks,
        ),
    }