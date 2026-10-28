from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def create_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = []

    for page in pages:
        for text in splitter.split_text(page["text"]):
            chunks.append({
                "text": text,
                "page": page["page"]
            })

    return chunks
