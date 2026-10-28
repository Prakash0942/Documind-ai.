from pathlib import Path


from docx import Document
import pymupdf

def load_document(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()
    pages = []

    if extension == ".pdf":
        with pymupdf.open(path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text")
                if text.strip():
                    pages.append({
                        "page": page_number,
                        "text": text
                    })

    elif extension == ".txt":
        text = path.read_text(
            encoding="utf-8", errors="replace"
        )
        pages.append({"page": 1, "text": text})

    elif extension == ".docx":
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        pages.append({"page": 1, "text": text})

    else:
        raise ValueError("Supported formats: PDF, TXT, DOCX")

    if not any(page["text"].strip() for page in pages):
        raise ValueError(
            "No text extracted. Scanned PDFs may require OCR."
        )

    return pages