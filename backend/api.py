
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from app.pipeline import DocumentIntelligence
from app.config import DOCUMENT_DIR
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="AI Document Intelligence API",
    description="Upload multiple documents and ask questions using RAG.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://documind-ai-mocha-xi.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCUMENTS_DIR = Path(DOCUMENT_DIR).resolve()
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per file

# Each document has its own independent RAG engine.
document_store = {}


class QuestionRequest(BaseModel):
    document_id: str = Field(
        min_length=1,
        description="ID of the document to search",
    )
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question about the selected document",
    )


@app.get("/")
def home():
    return {
        "message": "AI Document Intelligence API is running",
        "docs": "/docs",
        "endpoints": [
            "POST /documents/upload",
            "GET /documents",
            "POST /questions",
            "DELETE /documents/{document_id}",
        ],
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    original_name = Path(file.filename or "").name
    extension = Path(original_name).suffix.lower()

    if not original_name or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are supported.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 20 MB.",
        )

    document_id = uuid4().hex
    saved_name = f"{document_id}{extension}"
    file_path = DOCUMENTS_DIR / saved_name

    try:
        file_path.write_bytes(content)

        # Build a separate index for this document.
        engine = DocumentIntelligence()
        indexing_result = engine.index_document(str(file_path))

        # Register the document only after indexing succeeds.
        document_store[document_id] = {
            "filename": original_name,
            "path": str(file_path),
            "engine": engine,
            "details": indexing_result,
        }

        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "filename": original_name,
            "details": indexing_result,
        }

    except Exception as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(exc)}",
        ) from exc

    finally:
        await file.close()


@app.get("/documents")
def list_documents():
    return {
        "total_documents": len(document_store),
        "documents": [
            {
                "document_id": document_id,
                "filename": item["filename"],
                "details": item["details"],
            }
            for document_id, item in document_store.items()
        ],
    }


@app.post("/questions")
def ask_question(request: QuestionRequest):
    document = document_store.get(request.document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload it again or check its ID.",
        )

    try:
        result = document["engine"].ask(request.question)

        return {
            "document_id": request.document_id,
            "document": document["filename"],
            "question": request.question,
            "answer": result["answer"],
            "sources": result.get("sources", []),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(exc)}",
        ) from exc


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    document = document_store.pop(document_id, None)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = Path(document["path"])
    file_path.unlink(missing_ok=True)

    return {
        "message": "Document removed successfully.",
        "document_id": document_id,
        "filename": document["filename"],
    }

