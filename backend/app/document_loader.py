
from pathlib import Path

import pymupdf
from docx import Document


def load_document(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    pages = []

    # Check whether the file exists
    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    # Check whether the file is empty
    if path.stat().st_size == 0:
        raise ValueError("Uploaded document is empty.")

    # PDF processing
    if extension == ".pdf":

        try:
            with pymupdf.open(str(path)) as pdf:

                if pdf.is_encrypted:
                    raise ValueError(
                        "Password-protected PDFs are not supported."
                    )

                if len(pdf) == 0:
                    raise ValueError("PDF contains no pages.")

                for page_number, page in enumerate(pdf, start=1):
                    text = page.get_text("text")

                    if text and text.strip():
                        pages.append({
                            "page": page_number,
                            "text": text.strip()
                        })

        except pymupdf.FileDataError as exc:
            raise ValueError(
                "Invalid or corrupted PDF file."
            ) from exc

    # TXT processing
    elif extension == ".txt":

        text = path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        if text.strip():
            pages.append({
                "page": 1,
                "text": text.strip()
            })

    # DOCX processing
    elif extension == ".docx":

        doc = Document(str(path))

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        )

        if text.strip():
            pages.append({
                "page": 1,
                "text": text.strip()
            })

    else:
        raise ValueError(
            "Supported formats: PDF, TXT, DOCX"
        )

    # Validate extracted content
    if not pages:
        raise ValueError(
            "No text extracted from document. "
            "Scanned PDFs may require OCR."
        )

    return pages
