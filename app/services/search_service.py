from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.embeddings.encoder import SentenceTransformerEncoder
from app.indexing.faiss_store import FaissVectorStore
from app.indexing.metadata_store import MetadataStore
from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_loader import load_pdf
from app.retrieval.keyword import BM25KeywordSearcher
from app.retrieval.semantic import semantic_search
from app.schemas.document import UploadedDocumentSummary
from app.schemas.query import SearchQuery
from app.schemas.result import SearchResponse
from app.services.indexing_service import persist_indices


class SearchService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_directories()
        self.encoder = SentenceTransformerEncoder(settings.embedding_model)
        self.vector_store = FaissVectorStore.load(settings.vector_index_path)
        self.metadata_store = MetadataStore.load(settings.metadata_path)
        self.keyword_searcher = BM25KeywordSearcher()
        if self.metadata_store.records:
            self.keyword_searcher.fit(self.metadata_store.records)

    def ingest_document(
        self,
        pdf_path: Path,
        *,
        original_filename: str | None = None,
    ) -> UploadedDocumentSummary:
        pages = load_pdf(pdf_path)
        if not pages:
            raise ValueError("No extractable text was found in the uploaded PDF.")

        filename = original_filename or pdf_path.name
        document_id = f"{pdf_path.stem}-{uuid4().hex[:8]}"
        chunks = chunk_pages(
            pages,
            document_id=document_id,
            filename=filename,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        if not chunks:
            raise ValueError("The uploaded PDF could not be chunked into searchable text.")

        embeddings = self.encoder.encode_texts([chunk.text for chunk in chunks])
        self.vector_store.add(embeddings)
        self.metadata_store.add_chunks(chunks)
        self.keyword_searcher.fit(self.metadata_store.records)
        persist_indices(
            vector_store=self.vector_store,
            metadata_store=self.metadata_store,
            settings=self.settings,
        )

        return UploadedDocumentSummary(
            document_id=document_id,
            filename=filename,
            page_count=len(pages),
            chunk_count=len(chunks),
        )

    def search(self, payload: SearchQuery) -> SearchResponse:
        if not self.vector_store.is_ready() or not self.metadata_store.records:
            raise RuntimeError("No indexed document is available yet. Upload a PDF first.")

        top_k = payload.top_k or self.settings.top_k
        return semantic_search(
            payload.query,
            top_k=top_k,
            encoder=self.encoder,
            vector_store=self.vector_store,
            metadata_store=self.metadata_store,
        )


@lru_cache(maxsize=1)
def get_search_service() -> SearchService:
    return SearchService(get_settings())