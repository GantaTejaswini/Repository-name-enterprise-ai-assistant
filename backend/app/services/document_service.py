from pathlib import Path
import re

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader


CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

POPPLER_PATH = (
    r"C:\Users\hp\Downloads\Release-26.09.0-0"
    r"\poppler-26.09.0\Library\bin"
)

OCR_DPI = 300
OCR_PSM = 6


class DocumentService:

    def extract_text(self, file_path: str) -> list[dict]:
        path = Path(file_path)
        reader = PdfReader(path)

        pages = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text()

            if not text:
                continue

            text = self.clean_text(text)

            if not text:
                continue

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

        if pages:
            print(
                f"Normal PDF extraction found text "
                f"on {len(pages)} pages."
            )
            return pages

        print(
            "No extractable text found. "
            "Starting OCR fallback..."
        )

        return self.extract_text_with_ocr(
            file_path=file_path,
            total_pages=len(reader.pages),
        )

    def extract_text_with_ocr(
        self,
        file_path: str,
        total_pages: int,
    ) -> list[dict]:

        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

        pages = []

        print(
            f"Starting OCR for {total_pages} pages..."
        )

        for page_number in range(
            1,
            total_pages + 1,
        ):
            print(
                f"OCR processing page "
                f"{page_number}/{total_pages}..."
            )

            images = convert_from_path(
                file_path,
                first_page=page_number,
                last_page=page_number,
                dpi=OCR_DPI,
                poppler_path=POPPLER_PATH,
            )

            if not images:
                continue

            image = images[0]

            text = pytesseract.image_to_string(
                image,
                config=f"--psm {OCR_PSM}",
            )

            text = self.clean_text(text)

            if not text:
                continue

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

        print(
            f"OCR completed. Extracted text "
            f"from {len(pages)} pages."
        )

        return pages

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.replace(
            "\r\n",
            "\n",
        ).replace(
            "\r",
            "\n",
        )

        # Repair words split across PDF line breaks.
        # Example:
        # plat-
        # form
        # becomes:
        # platform
        text = re.sub(
            r"(?<=[A-Za-z])-\s*\n\s*(?=[A-Za-z])",
            "",
            text,
        )

        # Convert remaining line breaks to spaces.
        text = re.sub(
            r"\s*\n\s*",
            " ",
            text,
        )

        # Normalize repeated whitespace.
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = text.strip()

        return text

    def chunk_text(
        self,
        pages: list[dict],
    ) -> list[dict]:

        chunks = []

        for page in pages:

            page_number = page["page_number"]
            text = page["text"].strip()

            if not text:
                continue

            words = text.split()

            if not words:
                continue

            current_words = []
            current_length = 0

            chunk_word_lists = []

            for word in words:

                additional_length = len(word)

                if current_words:
                    additional_length += 1

                if (
                    current_words
                    and current_length
                    + additional_length
                    > CHUNK_SIZE
                ):
                    chunk_word_lists.append(
                        current_words
                    )

                    overlap_words = []
                    overlap_length = 0

                    for previous_word in reversed(
                        current_words
                    ):
                        word_length = len(
                            previous_word
                        )

                        if overlap_words:
                            word_length += 1

                        if (
                            overlap_length
                            + word_length
                            > CHUNK_OVERLAP
                        ):
                            break

                        overlap_words.insert(
                            0,
                            previous_word,
                        )

                        overlap_length += word_length

                    current_words = (
                        overlap_words.copy()
                    )

                    current_length = sum(
                        len(item)
                        for item in current_words
                    )

                    if current_words:
                        current_length += (
                            len(current_words) - 1
                        )

                current_words.append(word)

                if len(current_words) == 1:
                    current_length = len(word)
                else:
                    current_length += (
                        len(word) + 1
                    )

            if current_words:
                chunk_word_lists.append(
                    current_words
                )

            for word_list in chunk_word_lists:

                chunk_content = (
                    " ".join(word_list)
                    .strip()
                )

                if not chunk_content:
                    continue

                chunks.append(
                    {
                        "page_number": page_number,
                        "content": chunk_content,
                    }
                )

        print(
            f"Created {len(chunks)} "
            f"word-safe chunks."
        )

        return chunks