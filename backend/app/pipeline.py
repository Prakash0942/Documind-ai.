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
        chunks = create_chunks(pages)

        self.retriever.build_index(chunks)
        self.loaded = True

        return {
            "pages": len(pages),
            "chunks": len(chunks)
        }

    def ask(self, question):
        if not self.loaded:
            raise ValueError("Please index a document first.")

        results = self.retriever.search(question)
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