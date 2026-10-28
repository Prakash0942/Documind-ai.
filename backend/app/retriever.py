import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL, TOP_K


class DocumentRetriever:
    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        if not chunks:
            raise ValueError("No chunks to index.")

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        ).astype("float32")

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)
        self.chunks = chunks

    def search(self, question, top_k=TOP_K):
        if self.index is None:
            raise ValueError("Index a document before searching.")

        query_vector = self.embedding_model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

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