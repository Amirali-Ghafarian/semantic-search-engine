from pathlib import Path

import numpy as np
import pytest

import app.services.search_service as search_service_module
from app.core.config import Settings
from app.ingestion.pdf_loader import ExtractedPage
from app.schemas.query import SearchQuery


class FakeEncoder:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode_texts(self, texts: list[str]) -> np.ndarray:
        rows = []
        for text in texts:
            lowered = text.lower()
            vector = np.array(
                [
                    2.0 if "alpha" in lowered else 1.0,
                    2.0 if "beta" in lowered else 1.0,
                    float(max(len(lowered.split()), 1)),
                ],
                dtype=np.float32,
            )
            vector /= np.linalg.norm(vector)
            rows.append(vector)
        return np.vstack(rows).astype("float32")


def fake_load_pdf(_: Path) -> list[ExtractedPage]:
    return [
        ExtractedPage(page_number=1, text="alpha beta gamma delta epsilon zeta eta theta"),
        ExtractedPage(page_number=2, text="lambda mu alpha nu xi omicron pi rho sigma tau"),
    ]


def build_test_settings(tmp_path: Path) -> Settings:
    settings = Settings(
        embedding_model="test-model",
        chunk_size=4,
        chunk_overlap=1,
        top_k=2,
        data_dir=tmp_path / "data",
        raw_data_dir=tmp_path / "data" / "raw",
        processed_data_dir=tmp_path / "data" / "processed",
        index_dir=tmp_path / "data" / "indices",
    )
    settings.ensure_directories()
    return settings


def test_ingest_document_persists_index_and_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(search_service_module, "SentenceTransformerEncoder", FakeEncoder)
    monkeypatch.setattr(search_service_module, "load_pdf", fake_load_pdf)

    settings = build_test_settings(tmp_path)
    service = search_service_module.SearchService(settings)
    pdf_path = settings.raw_data_dir / "stored-paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%stub")

    summary = service.ingest_document(pdf_path, original_filename="paper.pdf")

    assert summary.filename == "paper.pdf"
    assert summary.page_count == 2
    assert summary.chunk_count > 0
    assert settings.vector_index_path.exists()
    assert settings.metadata_path.exists()

    reloaded_service = search_service_module.SearchService(settings)
    response = reloaded_service.search(SearchQuery(query="alpha", top_k=1))

    assert response.total_results == 1
    assert response.results[0].filename == "paper.pdf"
    assert response.results[0].page_number in {1, 2}


def test_search_requires_indexed_documents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(search_service_module, "SentenceTransformerEncoder", FakeEncoder)

    settings = build_test_settings(tmp_path)
    service = search_service_module.SearchService(settings)

    with pytest.raises(RuntimeError, match="Upload a PDF first"):
        service.search(SearchQuery(query="alpha"))