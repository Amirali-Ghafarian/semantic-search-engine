from app.indexing.faiss_store import FaissVectorStore
from app.indexing.metadata_store import MetadataStore
from app.schemas.result import SearchResponse, SearchResult


def semantic_search(
    query: str,
    *,
    top_k: int,
    encoder: object,
    vector_store: FaissVectorStore,
    metadata_store: MetadataStore,
) -> SearchResponse:
    query_embedding = encoder.encode_texts([query])
    scores, indices = vector_store.search(query_embedding, top_k)

    results: list[SearchResult] = []
    for rank, (score, chunk_id) in enumerate(zip(scores[0], indices[0]), start=1):
        if chunk_id < 0:
            continue

        metadata = metadata_store.get(int(chunk_id))
        if metadata is None:
            continue

        results.append(
            SearchResult(
                rank=rank,
                score=float(score),
                filename=metadata.filename,
                page_number=metadata.page_number,
                excerpt=metadata.text,
            )
        )

    return SearchResponse(query=query, total_results=len(results), results=results)