import asyncio
from pathlib import Path

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from app.core.elasticsearch import es_client


PDF_PATH = Path("../ingestion/resume.pdf")

MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"

INDEX_NAME = "document_chunks"

DOCUMENT_ID = "resume-demo-001"
TENANT_ID = "tenant-demo"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text, chunk_size=500, overlap=100):
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):

        target_end = start + chunk_size

        if target_end >= len(text):
            chunk = text[start:]

            if chunk.strip():
                chunks.append(chunk.strip())

            break

        end = text.rfind(" ", start, target_end)

        if end <= start:
            end = target_end

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def extract_chunks():

    reader = PdfReader(PDF_PATH)

    all_chunks = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        page_chunks = chunk_text(
            text,
            CHUNK_SIZE,
            CHUNK_OVERLAP
        )

        for chunk_number, chunk in enumerate(
            page_chunks,
            start=1
        ):

            all_chunks.append(
                {
                    "page_number": page_number,
                    "chunk_number": chunk_number,
                    "content": chunk,
                }
            )

    return all_chunks


async def main():

    print("=" * 80)
    print("PDF → CHUNKS → EMBEDDINGS → ELASTICSEARCH")
    print("=" * 80)

    print()
    print("Reading PDF...")

    chunks = extract_chunks()

    print("Total chunks:", len(chunks))

    print()
    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        trust_remote_code=True,
    )

    print("Model loaded successfully!")

    print()

    for chunk in chunks:

        page_number = chunk["page_number"]
        chunk_number = chunk["chunk_number"]
        content = chunk["content"]

        chunk_id = (
            f"{DOCUMENT_ID}-"
            f"page-{page_number}-"
            f"chunk-{chunk_number}"
        )

        print(
            f"Processing page {page_number}, "
            f"chunk {chunk_number}..."
        )

        # Generate embedding
        embedding = model.encode(
            content,
            normalize_embeddings=False,
        )

        print(
            "Embedding dimensions:",
            len(embedding)
        )

        # Elasticsearch document
        document = {
            "document_id": DOCUMENT_ID,
            "tenant_id": TENANT_ID,
            "filename": PDF_PATH.name,
            "page_number": page_number,
            "chunk_id": chunk_id,
            "content": content,
            "embedding": embedding.tolist(),
            "metadata": {
                "source": "pdf",
                "document_type": "resume",
            },
        }

        # Index into Elasticsearch
        response = await es_client.index(
            index=INDEX_NAME,
            id=chunk_id,
            document=document,
        )

        print(
            "Indexed:",
            response["result"]
        )

        print("-" * 80)

    # Make documents immediately searchable
    await es_client.indices.refresh(
        index=INDEX_NAME
    )

    # Verify document count
    count_response = await es_client.count(
        index=INDEX_NAME
    )

    print()
    print("=" * 80)
    print("INDEXING COMPLETE")
    print("=" * 80)

    print(
        "Documents currently in index:",
        count_response["count"]
    )

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())