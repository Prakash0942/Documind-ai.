from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def create_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = []

    for page in pages:
        text = page.get("text", "").strip()

        if not text:
            continue

        for chunk in splitter.split_text(text):
            chunks.append({
                "text": chunk,
                "page": page["page"]
            })

    if not chunks:
        raise ValueError("No valid text chunks were created.")

    return chunks