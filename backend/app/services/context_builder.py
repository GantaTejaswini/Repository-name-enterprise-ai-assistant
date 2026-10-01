from typing import Any


def build_context(results: list[dict[str, Any]]) -> str:
    """
    Convert retrieval results into a clean context
    that can be provided to the LLM.
    """

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
SOURCE {index}
Document: {result["filename"]}
Page: {result["page_number"]}
Chunk ID: {result["chunk_id"]}

Content:
{result["content"]}
""".strip()
        )

    return "\n\n".join(context_parts)