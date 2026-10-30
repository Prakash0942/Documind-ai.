

from app.document_loader import load_document
from app.chunker import create_chunks
from app.retriever import DocumentRetriever
from app.llm import generate_answer


class DocumentIntelligence:

    def __init__(self):
        self.retriever = DocumentRetriever()
        self.loaded = False

    def index_document(self, file_path):

        pages = load_document(file_path)

        if not pages:
            raise ValueError("No pages extracted from document.")

        chunks = create_chunks(pages)

        if not chunks:
            raise ValueError("No text chunks generated.")

        self.retriever.build_index(chunks)

        self.loaded = True

        return {
            "pages": len(pages),
            "chunks": len(chunks)
        }

    def ask(self, question):

        if not self.loaded:
            raise ValueError("Please index a document first.")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        results = self.retriever.search(question)

        if not results:
            raise ValueError(
                "No relevant information found in the document."
            )

        answer = generate_answer(question, results)

        return {
            "answer": answer,
            "sources": [
                {
                    "page": item["page"],
                    "similarity": round(item["score"], 3),
                    "text": item["text"]
                }
                for item in results
            ]
        }
