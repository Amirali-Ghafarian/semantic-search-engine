from pathlib import Path
from typing import Any

import numpy as np


class FaissVectorStore:
    def __init__(self) -> None:
        self._index: Any | None = None
        self.dimension: int | None = None

    def _faiss(self) -> Any:
        import faiss

        return faiss

    @property
    def index(self) -> Any | None:
        return self._index

    def is_ready(self) -> bool:
        return self._index is not None and self._index.ntotal > 0

    def add(self, embeddings: np.ndarray) -> None:
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D numpy array.")

        faiss = self._faiss()
        if self._index is None:
            self.dimension = int(embeddings.shape[1])
            self._index = faiss.IndexFlatIP(self.dimension)

        self._index.add(embeddings)

    def search(self, query_embedding: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        if not self.is_ready():
            raise RuntimeError("The vector index is empty.")
        return self._index.search(query_embedding, top_k)

    def save(self, destination: Path) -> None:
        if self._index is None:
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._faiss().write_index(self._index, str(destination))

    @classmethod
    def load(cls, source: Path) -> "FaissVectorStore":
        store = cls()
        if source.exists():
            store._index = store._faiss().read_index(str(source))
            store.dimension = store._index.d
        return store