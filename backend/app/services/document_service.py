from pathlib import Path
import re

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader


CHUNK_SIZE = 700
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

        # Preserve useful paragraph/list boundaries.
        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        text = text.strip()

        return text

    def _split_long_block(
        self,
        text: str,
    ) -> list[str]:
        words = text.split()

        if not words:
            return []

        chunks = []
        current_words = []
        current_length = 0

        for word in words:
            additional_length = len(word)

            if current_words:
                additional_length += 1

            if (
                current_words
                and current_length + additional_length
                > CHUNK_SIZE
            ):
                chunks.append(
                    " ".join(current_words).strip()
                )

                overlap_words = []
                overlap_length = 0

                for previous_word in reversed(
                    current_words
                ):
                    word_length = len(previous_word)

                    if overlap_words:
                        word_length += 1

                    if (
                        overlap_length + word_length
                        > CHUNK_OVERLAP
                    ):
                        break

                    overlap_words.insert(
                        0,
                        previous_word,
                    )

                    overlap_length += word_length

                current_words = overlap_words.copy()

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
                current_length += len(word) + 1

        if current_words:
            chunks.append(
                " ".join(current_words).strip()
            )

        return chunks

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

            # Split on paragraph-like boundaries first.
            # This helps preserve sections and lists.
            blocks = re.split(
                r"\n\s*\n+",
                text,
            )

            page_blocks = []

            for block in blocks:
                block = block.strip()

                if not block:
                    continue

                page_blocks.append(block)

            current_block_words = []
            current_block_length = 0

            for block in page_blocks:
                block_words = block.split()

                if not block_words:
                    continue

                block_length = len(block)

                # If adding the complete logical block keeps
                # the chunk within the target size, keep it intact.
                if (
                    current_block_words
                    and current_block_length
                    + 1
                    + block_length
                    <= CHUNK_SIZE
                ):
                    current_block_words.extend(
                        block_words
                    )
                    current_block_length += (
                        1 + block_length
                    )
                    continue

                # Flush the current logical chunk.
                if current_block_words:
                    chunk_content = " ".join(
                        current_block_words
                    ).strip()

                    if chunk_content:
                        chunks.append(
                            {
                                "page_number": page_number,
                                "content": chunk_content,
                            }
                        )

                    overlap_words = []
                    overlap_length = 0

                    for previous_word in reversed(
                        current_block_words
                    ):
                        word_length = len(previous_word)

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

                    current_block_words = (
                        overlap_words.copy()
                    )

                    current_block_length = sum(
                        len(word)
                        for word in current_block_words
                    )

                    if current_block_words:
                        current_block_length += (
                            len(current_block_words) - 1
                        )

                # Keep a logical block intact when possible.
                if block_length <= CHUNK_SIZE:
                    current_block_words.extend(
                        block_words
                    )
                    current_block_length += (
                        block_length
                        if not current_block_words[
                            : -len(block_words)
                        ]
                        else block_length
                    )

                    if (
                        len(current_block_words)
                        > len(block_words)
                    ):
                        current_block_length += 1

                else:
                    # A very large logical block must still
                    # be safely split.
                    long_chunks = self._split_long_block(
                        block
                    )

                    for long_chunk in long_chunks:
                        if not long_chunk:
                            continue

                        chunks.append(
                            {
                                "page_number": page_number,
                                "content": long_chunk,
                            }
                        )

                    current_block_words = []
                    current_block_length = 0

            if current_block_words:
                chunk_content = " ".join(
                    current_block_words
                ).strip()

                if chunk_content:
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