from dataclasses import dataclass

from evaluation.dataset import TENANT_A_ID


@dataclass(frozen=True)
class AnswerEvaluationCase:
    question: str
    reference_answer: str
    expected_phrases: tuple[str, ...]
    relevant_chunk_ids: tuple[str, ...]


ANSWER_EVALUATION_CASES = [
    AnswerEvaluationCase(
        question="What programming skills are listed?",
        reference_answer=(
            "The programming skills listed are Python, MySQL, "
            "C, Java, and PHP."
        ),
        expected_phrases=(
            "Python",
            "MySQL",
            "C",
            "Java",
            "PHP",
        ),
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-2",
        ),
    ),
    AnswerEvaluationCase(
        question=(
            "Which machine learning and deep learning "
            "algorithms are listed?"
        ),
        reference_answer=(
            "The listed algorithms include Logistic Regression, "
            "Decision Tree, Random Forest, SVM, KNN, Naive Bayes, "
            "CNN, RNN, LSTM, and Attention Mechanism."
        ),
        expected_phrases=(
            "Logistic Regression",
            "Decision Tree",
            "Random Forest",
            "SVM",
            "KNN",
            "Naive Bayes",
            "CNN",
            "RNN",
            "LSTM",
            "Attention Mechanism",
        ),
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-3",
        ),
    ),
    AnswerEvaluationCase(
        question="What certifications are listed?",
        reference_answer=(
            "The certifications listed are Cloud Computing from "
            "NPTEL IIT Kharagpur, AI First Software Engineering, "
            "and AWS Cloud Practitioner Essentials."
        ),
        expected_phrases=(
            "Cloud Computing",
            "NPTEL",
            "IIT Kharagpur",
            "AI First Software Engineering",
            "AWS Cloud Practitioner Essentials",
        ),
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-4",
        ),
    ),
    AnswerEvaluationCase(
        question="What was the AI-based Solar Optimization System project?",
        reference_answer=(
            "The AI-based Solar Optimization System used ESP32 "
            "and sensors for real-time data simulation, machine "
            "learning predictions through Flask APIs, and a "
            "cloud-based ThingsBoard dashboard."
        ),
        expected_phrases=(
            "ESP32",
            "sensors",
            "Flask",
            "ThingsBoard",
        ),
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-6",
        ),
    ),
    AnswerEvaluationCase(
        question="What project involved detecting Chronic Kidney Disease?",
        reference_answer=(
            "The Chronic Kidney Disease project involved an "
            "ML model that analyzed patient reports to detect "
            "Chronic Kidney Disease."
        ),
        expected_phrases=(
            "ML model",
            "patient",
            "Chronic Kidney Disease",
        ),
        relevant_chunk_ids=(
            "8520cfdd-6fde-431f-a822-ce3771dce572-chunk-7",
        ),
    ),
]


__all__ = [
    "TENANT_A_ID",
    "AnswerEvaluationCase",
    "ANSWER_EVALUATION_CASES",
]