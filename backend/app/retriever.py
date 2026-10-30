



import faiss
import numpy as np

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, TOP_K


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768
BATCH_SIZE = 16


class DocumentRetriever:

    _client = None

    def __init__(self):
        self.index = None
        self.chunks = []

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is missing.")

            cls._client = genai.Client(
                api_key=GEMINI_API_KEY
            )

        return cls._client

    @classmethod
    def _generate_embeddings(cls, texts, task_type):
        client = cls._get_client()
        all_embeddings = []

        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]

            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=EMBEDDING_DIMENSION
                )
            )

            if not response.embeddings:
                raise ValueError("Google returned no embeddings.")

            for item in response.embeddings:
                all_embeddings.append(item.values)

        embeddings = np.asarray(
            all_embeddings,
            dtype=np.float32
        )

        if embeddings.shape != (
            len(texts),
            EMBEDDING_DIMENSION
        ):
            raise ValueError("Unexpected embedding dimensions.")

        faiss.normalize_L2(embeddings)

        return embeddings

    def build_index(self, chunks):
        if not chunks:
            raise ValueError("No chunks to index.")

        self.chunks = [
            chunk for chunk in chunks
            if chunk.get("text", "").strip()
        ]

        if not self.chunks:
            raise ValueError("No valid text chunks found.")

        texts = [
            chunk["text"] for chunk in self.chunks
        ]

        embeddings = self._generate_embeddings(
            texts,
            "RETRIEVAL_DOCUMENT"
        )

        self.index = faiss.IndexFlatIP(
            EMBEDDING_DIMENSION
        )

        self.index.add(embeddings)

    def search(self, question, top_k=TOP_K):
        if self.index is None:
            raise ValueError("Index a document before searching.")

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        query_embeddings = self._generate_embeddings(
            [question],
            "RETRIEVAL_QUERY"
        )

        scores, indices = self.index.search(
            query_embeddings,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                result = dict(self.chunks[int(idx)])
                result["score"] = float(score)
                results.append(result)

        return results
