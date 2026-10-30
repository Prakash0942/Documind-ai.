
import gc

from app.document_loader import load_document
from app.chunker import create_chunks
from app.retriever import DocumentRetriever
from app.llm import generate_answer


class DocumentIntelligence:

    def __init__(self):
        self.retriever = DocumentRetriever()
        self.loaded = False

    def index_document(self, file_path):

        # Step 1: Extract document text
        pages = load_document(file_path)

        if not pages:
            raise ValueError("No pages extracted from document.")

        # Step 2: Split document into chunks
        chunks = create_chunks(pages)

        if not chunks:
            raise ValueError("No text chunks generated.")

        # Step 3: Build FAISS index
        self.retriever.build_index(chunks)

        self.loaded = True

        result = {
            "pages": len(pages),
            "chunks": len(chunks)
        }

        # Release temporary references
        del pages
        del chunks
        gc.collect()

        return result

    def ask(self, question):

        if not self.loaded:
            raise ValueError(
                "Please index a document first."
            )

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        # Step 1: Retrieve relevant chunks
        results = self.retriever.search(question)

        if not results:
            raise ValueError(
                "No relevant information found in the document."
            )

        # Step 2: Generate answer using Gemini
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
