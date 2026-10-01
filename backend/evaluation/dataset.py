from dataclasses import dataclass


TENANT_A_ID = "9984bc36-f841-44bd-899a-2a62c755f5ec"


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    relevant_chunk_ids: tuple[str, ...]


EVALUATION_CASES = [
    EvaluationCase(
        question="What programming skills are listed?",
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-2",
        ),
    ),
    EvaluationCase(
        question="Which machine learning and deep learning algorithms are listed?",
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-3",
        ),
    ),
    EvaluationCase(
        question="What certifications are listed?",
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-4",
        ),
    ),
    EvaluationCase(
        question="What was the AI-based Solar Optimization System project?",
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-6",
        ),
    ),
    EvaluationCase(
        question="What project involved detecting Chronic Kidney Disease?",
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-7",
        ),
    ),
]