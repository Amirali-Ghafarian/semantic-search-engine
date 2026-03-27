from app.indexing.metadata_store import ChunkMetadata


class BM25KeywordSearcher:
    def __init__(self) -> None:
        self._bm25 = None
        self._corpus: list[list[str]] = []

    def fit(self, records: list[ChunkMetadata]) -> None:
        from rank_bm25 import BM25Okapi

        self._corpus = [record.text.lower().split() for record in records]
        self._bm25 = BM25Okapi(self._corpus) if self._corpus else None

    def search(self, query: str, top_k: int) -> list[tuple[int, float]]:
        if self._bm25 is None:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)
        ranked_indices = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)
        return [(idx, float(scores[idx])) for idx in ranked_indices[:top_k]]