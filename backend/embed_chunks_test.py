import asyncio
from pathlib import Path

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from app.core.elasticsearch import es_client


PDF_PATH = Path("../ingestion/resume.pdf")

MODEL_NAME = "nvidia/llama-nemotron-embed-1b-v2"

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

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"Generating embedding "
            f"{index}/{len(chunks)}..."
        )

        embedding = model.encode(
            chunk["content"],
            normalize_embeddings=False,
        )

        print(
            "Embedding shape:",
            embedding.shape
        )

    await es_client.close()


if __name__ == "__main__":
    asyncio.run(main())