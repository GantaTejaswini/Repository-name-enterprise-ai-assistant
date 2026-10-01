from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path("../ingestion/resume.pdf")

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

        # Find the nearest whitespace before the target limit.
        end = text.rfind(" ", start, target_end)

        if end <= start:
            end = target_end

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        # Move forward while keeping overlap.
        start = end - overlap

    return chunks


def main():

    print("Reading PDF:")
    print(PDF_PATH.resolve())
    print()

    if not PDF_PATH.exists():
        print("ERROR: PDF file not found.")
        return

    reader = PdfReader(PDF_PATH)

    all_chunks = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        page_chunks = chunk_text(
            text,
            CHUNK_SIZE,
            CHUNK_OVERLAP,
        )

        for chunk_number, chunk in enumerate(
            page_chunks,
            start=1,
        ):

            chunk_data = {
                "page_number": page_number,
                "chunk_number": chunk_number,
                "content": chunk,
            }

            all_chunks.append(chunk_data)

    print("Total pages:", len(reader.pages))
    print("Total chunks:", len(all_chunks))
    print()

    for chunk in all_chunks:

        print("=" * 80)
        print(
            f"PAGE {chunk['page_number']} | "
            f"CHUNK {chunk['chunk_number']}"
        )
        print("=" * 80)

        print(chunk["content"])
        print()


if __name__ == "__main__":
    main()