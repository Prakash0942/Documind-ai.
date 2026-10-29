
import faiss
import numpy as np

from app.config import EMBEDDING_MODEL, TOP_K


class DocumentRetriever:
    def __init__(self):
        self.embedding_model = None
        self.index = None
        self.chunks = []

    def _get_embedding_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer

            self.embedding_model = SentenceTransformer(
                EMBEDDING_MODEL,
                device="cpu"
            )

        return self.embedding_model

    def build_index(self, chunks):
        if not chunks:
            raise ValueError("No chunks to index.")

        model = self._get_embedding_model()
        texts = [chunk["text"] for chunk in chunks]
        embedding_batches = []

        batch_size = 8

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

        embeddings = np.concatenate(embedding_batches, axis=0)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)
        self.chunks = chunks

    def search(self, question, top_k=TOP_K):
        if self.index is None:
            raise ValueError("Index a document before searching.")

        model = self._get_embedding_model()

        query_vector = model.encode(
            [question],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
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
