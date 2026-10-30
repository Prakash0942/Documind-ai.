

import faiss
import numpy as np

from app.config import EMBEDDING_MODEL, TOP_K


class DocumentRetriever:

    # Shared model across all document retrievers
    _embedding_model = None

    def __init__(self):
        self.index = None
        self.chunks = []

    @classmethod
    def _get_embedding_model(cls):
        if cls._embedding_model is None:
            from sentence_transformers import SentenceTransformer

            cls._embedding_model = SentenceTransformer(
                EMBEDDING_MODEL,
                device="cpu"
            )

        return cls._embedding_model

    def build_index(self, chunks):
        if not chunks:
            raise ValueError("No chunks to index.")

        model = self._get_embedding_model()

        texts = [
            chunk["text"]
            for chunk in chunks
            if chunk.get("text", "").strip()
        ]

        if not texts:
            raise ValueError("No valid text chunks found.")

        embedding_batches = []

        # Smaller batches reduce peak memory usage
        batch_size = 2

        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]

            embeddings = model.encode(
                batch,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=batch_size
            )

            embedding_batches.append(
                np.asarray(embeddings, dtype=np.float32)
            )

        embeddings = np.concatenate(
            embedding_batches,
            axis=0
        )

        self.index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        self.index.add(embeddings)

        # Keep only chunks corresponding to embedded texts
        self.chunks = [
            chunk for chunk in chunks
            if chunk.get("text", "").strip()
        ]

    def search(self, question, top_k=TOP_K):
        if self.index is None:
            raise ValueError(
                "Index a document before searching."
            )

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        model = self._get_embedding_model()

        query_vector = model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=1
        ).astype(np.float32)

        scores, indices = self.index.search(
            query_vector,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                result = dict(self.chunks[int(idx)])
                result["score"] = float(score)
                results.append(result)

        return results
