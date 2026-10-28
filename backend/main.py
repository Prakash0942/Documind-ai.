from pathlib import Path

from app.config import DOCUMENT_DIR
from app.pipeline import DocumentIntelligence


def main():
    Path(DOCUMENT_DIR).mkdir(parents=True, exist_ok=True)

    print("\n=== AI DOCUMENT INTELLIGENCE ===")
    print("Supported formats: PDF, TXT, DOCX")

    file_name = input(
        "Enter filename from documents folder: "
    ).strip().strip('"')

    # Accept only a filename inside the documents directory.
    file_path = (Path(DOCUMENT_DIR) / file_name).resolve()

    if file_path.parent != Path(DOCUMENT_DIR).resolve():
        raise ValueError("Enter a filename inside documents.")

    if not file_path.is_file():
        print(f"File not found: {file_path}")
        return

    app = DocumentIntelligence()

    try:
        stats = app.index_document(str(file_path))
        print(f"\nDocument indexed: {stats['pages']} pages")
        print(f"Chunks created: {stats['chunks']}")

        while True:
            question = input(
                "\nAsk a question (or type exit): "
            ).strip()

            if question.lower() == "exit":
                break

            if not question:
                continue

            try:
                result = app.ask(question)

                print("\nANSWER:\n")
                print(result["answer"])

                print("\nSOURCES:")
                for source in result["sources"]:
                    print(
                        f"Page {source['page']} | "
                        f"Similarity: {source['similarity']}"
                    )
                    print(source["text"][:250])
            except Exception as error:
                print(
                    f"Question failed: {type(error).__name__}: {error}"
                )

    except Exception as error:
        print(f"Project failed: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()