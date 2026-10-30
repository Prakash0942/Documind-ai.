


import os

# Limit CPU thread usage on Render
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import faiss
import numpy as np

from app.config import EMBEDDING_MODEL, TOP_K


class DocumentRetriever:

    # Load the embedding model only once
    _embedding_model = None

    def __init__(self):
        self.index = None
        self.chunks = []

    @classmethod
    def _get_embedding_model(cls):
        if cls._embedding_model is None:
            import torch
            from sentence_transformers import SentenceTransformer

            torch.set_num_threads(1)

            cls._embedding_model = SentenceTransformer(
                EMBEDDING_MODEL,
                device="cpu"
            )

            cls._embedding_model.eval()

        return cls._embedding_model

    def build_index(self, chunks):
        if not chunks:
            raise ValueError("No chunks to index.")

        model = self._get_embedding_model()

        valid_chunks = [
            chunk for chunk in chunks
            if chunk.get("text", "").strip()
        ]

        if not valid_chunks:
            raise ValueError("No valid text chunks found.")

        self.chunks = valid_chunks

        batch_size = 1
        embedding_batches = []

        for start in range(0, len(self.chunks), batch_size):
            batch_chunks = self.chunks[start:start + batch_size]

            texts = [
                chunk["text"]
                for chunk in batch_chunks
            ]

            embeddings = model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=1
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

    def search(self, question, top_k=TOP_K):
        if self.index is None:
            raise ValueError("Index a document before searching.")

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
