from app.core.config import Settings
from app.indexing.faiss_store import FaissVectorStore
from app.indexing.metadata_store import MetadataStore


def persist_indices(
    *,
    vector_store: FaissVectorStore,
    metadata_store: MetadataStore,
    settings: Settings,
) -> None:
    vector_store.save(settings.vector_index_path)
    metadata_store.save(settings.metadata_path)