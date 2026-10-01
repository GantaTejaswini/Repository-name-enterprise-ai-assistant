from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path("../ingestion/resume.pdf")


def main():

    print("Reading PDF:")
    print(PDF_PATH.resolve())
    print()

    if not PDF_PATH.exists():
        print("ERROR: PDF file not found.")
        return

    reader = PdfReader(PDF_PATH)

    print("Total pages:", len(reader.pages))
    print()

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        print("=" * 80)
        print(f"PAGE {page_number}")
        print("=" * 80)

        print(text[:2000])

        print()


if __name__ == "__main__":
    main()