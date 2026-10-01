import re
import time
from typing import Any

import torch


class LLMService:
    """
    Central LLM runtime.

    Providers:
    - extractive: CPU-friendly development mode.
    - granite: IBM Granite 3.3 8B local model.

    The RAG pipeline does not need to know which provider is active.
    """

    STOP_WORDS = {
        "what",
        "which",
        "who",
        "where",
        "when",
        "why",
        "how",
        "is",
        "are",
        "was",
        "were",
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "in",
        "on",
        "for",
        "to",
        "from",
        "listed",
        "project",
        "projects",
        "involved",
        "describe",
        "tell",
        "me",
        "about",
        "does",
        "did",
        "do",
        "this",
        "that",
        "their",
        "there",
    }

    def __init__(
        self,
        provider: str,
        tokenizer: Any = None,
        model: Any = None,
    ):
        self.provider = provider.lower().strip()
        self.tokenizer = tokenizer
        self.model = model

        if self.provider not in {"extractive", "granite"}:
            raise ValueError(
                f"Unsupported LLM_PROVIDER: {self.provider}"
            )

        if self.provider == "granite":
            if self.tokenizer is None or self.model is None:
                raise ValueError(
                    "Granite provider requires tokenizer and model."
                )

            self.model.eval()

        print(f"LLM provider: {self.provider}")

    async def generate(
        self,
        question: str,
        context: str,
        prompt: str,
    ) -> dict[str, Any]:

        if self.provider == "extractive":
            return self._generate_extractive(
                question=question,
                context=context,
            )

        return self._generate_granite(prompt)

    @classmethod
    def _question_terms(
        cls,
        question: str,
    ) -> set[str]:

        words = re.findall(
            r"[a-zA-Z][a-zA-Z0-9-]+",
            question.lower(),
        )

        return {
            word
            for word in words
            if word not in cls.STOP_WORDS
            and len(word) > 1
        }

    @staticmethod
    def _parse_sources(
        context: str,
    ) -> list[str]:

        sections = re.split(
            r"\n\s*SOURCE\s+\d+\s*\n",
            context,
            flags=re.IGNORECASE,
        )

        return [
            section.strip()
            for section in sections
            if section.strip()
        ]

    @staticmethod
    def _extract_content(
        source: str,
    ) -> str:

        match = re.search(
            r"Content:\s*(.*)",
            source,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if match:
            return match.group(1).strip()

        return source.strip()

    @staticmethod
    def _clean_text(
        text: str,
    ) -> str:

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        text = re.sub(
            r"\s+([,.;:)])",
            r"\1",
            text,
        )

        text = re.sub(
            r"([(])\s+",
            r"\1",
            text,
        )

        return text

    @classmethod
    def _split_inline_sections(
        cls,
        content: str,
    ) -> list[tuple[str, str]]:
        """
        Split OCR text around short inline section labels.

        OCR often collapses several resume sections onto
        the same physical line. We therefore recognize
        short labels such as:

        Programming Skills:
        Machine Learning & Deep Learning:
        Certifications:

        The label is deliberately limited to five words
        so that ordinary resume text is not mistaken for
        a section heading.
        """

        text = cls._clean_text(content)

        label_pattern = re.compile(
            r"(?P<label>"
            r"[A-Za-z][A-Za-z0-9&/+.\\-]*"
            r"(?:\s+[A-Za-z][A-Za-z0-9&/+.\\-]*){0,4}"
            r")"
            r"\s*:\s*"
        )

        matches = list(
            label_pattern.finditer(text)
        )

        sections: list[tuple[str, str]] = []

        for index, match in enumerate(matches):

            label = match.group(
                "label"
            ).strip()

            start = match.end()

            if index + 1 < len(matches):
                end = matches[
                    index + 1
                ].start()
            else:
                end = len(text)

            body = text[
                start:end
            ].strip(" .-")

            if not body:
                continue

            if len(label) > 70:
                continue

            sections.append(
                (
                    label,
                    body,
                )
            )

        return sections

    @staticmethod
    def _sentence_split(
        text: str,
    ) -> list[str]:

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if not text:
            return []

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    @staticmethod
    def _term_score(
        text: str,
        terms: set[str],
    ) -> int:

        words = set(
            re.findall(
                r"[a-zA-Z][a-zA-Z0-9-]+",
                text.lower(),
            )
        )

        return len(
            words.intersection(terms)
        )

    @staticmethod
    def _phrase_score(
        text: str,
        question: str,
    ) -> int:

        normalized_text = re.sub(
            r"[^a-z0-9]+",
            " ",
            text.lower(),
        )

        normalized_question = re.sub(
            r"[^a-z0-9]+",
            " ",
            question.lower(),
        )

        question_words = normalized_question.split()

        if not question_words:
            return 0

        score = 0

        for size in (4, 3, 2):

            if len(question_words) < size:
                continue

            for index in range(
                len(question_words) - size + 1
            ):

                phrase = " ".join(
                    question_words[
                        index:index + size
                    ]
                )

                if phrase in normalized_text:
                    score += size

        return score

    @classmethod
    def _best_section_answer(
        cls,
        question: str,
        sections: list[tuple[str, str]],
    ) -> str | None:

        terms = cls._question_terms(
            question
        )

        if not terms or not sections:
            return None

        candidates = []

        for index, (
            label,
            body,
        ) in enumerate(sections):

            label_term_score = cls._term_score(
                label,
                terms,
            )

            body_term_score = cls._term_score(
                body,
                terms,
            )

            label_phrase_score = cls._phrase_score(
                label,
                question,
            )

            body_phrase_score = cls._phrase_score(
                body,
                question,
            )

            score = (
                label_phrase_score * 20
                + label_term_score * 12
                + body_phrase_score * 6
                + min(body_term_score, 5)
                - index * 0.01
            )

            candidates.append(
                (
                    score,
                    label_term_score,
                    body_term_score,
                    label_phrase_score,
                    body_phrase_score,
                    -index,
                    label,
                    body,
                )
            )

        candidates.sort(
            reverse=True
        )

        best = candidates[0]

        if best[0] <= 0:
            return None

        # A section should be selected because its label
        # itself matches the question. This prevents a
        # generic section such as "Subject of Interest"
        # from winning merely because its body contains
        # the words "Machine Learning".
        if (
            best[1] == 0
            and best[3] == 0
        ):
            return None

        return cls._clean_text(
            best[7]
        )

    @classmethod
    def _best_sentence_window(
        cls,
        question: str,
        content: str,
    ) -> str | None:

        terms = cls._question_terms(
            question
        )

        sentences = cls._sentence_split(
            content
        )

        if not terms or not sentences:
            return None

        scored = []

        for index, sentence in enumerate(
            sentences
        ):

            score = cls._term_score(
                sentence,
                terms,
            )

            phrase_score = cls._phrase_score(
                sentence,
                question,
            )

            total_score = (
                score
                + phrase_score * 4
            )

            if total_score:

                scored.append(
                    (
                        total_score,
                        -index,
                        index,
                        sentence,
                    )
                )

        if not scored:
            return None

        scored.sort(
            reverse=True
        )

        (
            _,
            _,
            best_index,
            best_sentence,
        ) = scored[0]

        selected_indexes = {
            best_index
        }

        for neighbor_index in (
            best_index - 1,
            best_index + 1,
        ):

            if (
                0
                <= neighbor_index
                < len(sentences)
            ):

                neighbor = sentences[
                    neighbor_index
                ]

                if (
                    cls._term_score(
                        neighbor,
                        terms,
                    )
                    >= 1
                ):
                    selected_indexes.add(
                        neighbor_index
                    )

        return " ".join(
            sentences[index]
            for index in sorted(
                selected_indexes
            )
        )

    @classmethod
    def _select_relevant_content(
        cls,
        question: str,
        context: str,
    ) -> str:

        sources = cls._parse_sources(
            context
        )

        if not sources:
            return ""

        source_candidates = []

        terms = cls._question_terms(
            question
        )

        for source_index, source in enumerate(
            sources
        ):

            content = cls._extract_content(
                source
            )

            sections = (
                cls._split_inline_sections(
                    content
                )
            )

            section_answer = (
                cls._best_section_answer(
                    question,
                    sections,
                )
            )

            if section_answer:

                answer_score = (
                    cls._term_score(
                        section_answer,
                        terms,
                    )
                )

                source_candidates.append(
                    (
                        100
                        + answer_score,
                        -source_index,
                        section_answer,
                    )
                )

                continue

            sentence_answer = (
                cls._best_sentence_window(
                    question,
                    content,
                )
            )

            if sentence_answer:

                answer_score = (
                    cls._term_score(
                        sentence_answer,
                        terms,
                    )
                )

                source_candidates.append(
                    (
                        answer_score,
                        -source_index,
                        sentence_answer,
                    )
                )

        if not source_candidates:
            return ""

        source_candidates.sort(
            reverse=True
        )

        return cls._clean_text(
            source_candidates[0][2]
        )

    def _generate_extractive(
        self,
        question: str,
        context: str,
    ) -> dict[str, Any]:

        generation_start = time.perf_counter()

        cleaned_context = context.strip()

        if not cleaned_context:

            answer = (
                "The information is not available "
                "in the provided documents."
            )

        else:

            selected_text = (
                self._select_relevant_content(
                    question=question,
                    context=cleaned_context,
                )
            )

            if not selected_text:

                answer = (
                    "The information is not available "
                    "in the provided documents."
                )

            else:

                if len(selected_text) > 1200:

                    selected_text = (
                        selected_text[:1200]
                        .rsplit(" ", 1)[0]
                        + "..."
                    )

                answer = selected_text

        generation_time = (
            time.perf_counter()
            - generation_start
        )

        return {
            "answer": answer,
            "generation_seconds": round(
                generation_time,
                3,
            ),
            "provider": "extractive",
        }

    def _generate_granite(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        input_text = (
            self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        )

        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
        )

        prompt_token_count = (
            inputs["input_ids"].shape[1]
        )

        print(
            f"RAG prompt tokens: "
            f"{prompt_token_count}"
        )

        print(
            "Testing Granite generation..."
        )

        generation_start = time.perf_counter()

        with torch.inference_mode():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=128,
                do_sample=False,
                use_cache=True,
            )

        generation_time = (
            time.perf_counter()
            - generation_start
        )

        print(
            "Granite generation completed in "
            f"{generation_time:.3f} seconds"
        )

        generated_tokens = outputs[0][
            prompt_token_count:
        ]

        answer = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

        return {
            "answer": answer,
            "generation_seconds": round(
                generation_time,
                3,
            ),
            "provider": "granite",
        }