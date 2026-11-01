
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def create_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",  # Paragraph boundary
            "\n",    # Line boundary
            ". ",    # Sentence boundary
            "? ",
            "! ",
            "; ",
            ": ",
            " ",     # Word boundary
            ""       # Character boundary as final fallback
        ],
        keep_separator=True,
        strip_whitespace=True,
        length_function=len
    )

    chunks = []

    for page in pages:
        text = page.get("text", "").strip()
        page_number = page.get("page")

        if not text:
            continue

        page_chunks = splitter.split_text(text)

        for chunk in page_chunks:
            cleaned_chunk = chunk.strip()

            if not cleaned_chunk:
                continue

            chunks.append({
                "text": cleaned_chunk,
                "page": page_number
            })

    if not chunks:
        raise ValueError("No valid text chunks were created.")

    return chunks
