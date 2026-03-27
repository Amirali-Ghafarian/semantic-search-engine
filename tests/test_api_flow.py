from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.routes import upload as upload_routes
from app.core.config import Settings
from app.schemas.document import UploadedDocumentSummary
from app.schemas.query import SearchQuery
from app.schemas.result import SearchResponse, SearchResult
from app.services.search_service import get_search_service


class StubSearchService:
    def __init__(self) -> None:
        self.ingested_paths: list[Path] = []
        self.original_filenames: list[str | None] = []

    def ingest_document(
        self,
        pdf_path: Path,
        *,
        original_filename: str | None = None,
    ) -> UploadedDocumentSummary:
        self.ingested_paths.append(pdf_path)
        self.original_filenames.append(original_filename)
        return UploadedDocumentSummary(
            document_id="doc-123",
            filename=original_filename or pdf_path.name,
            page_count=2,
            chunk_count=4,
        )

    def search(self, payload: SearchQuery) -> SearchResponse:
        return SearchResponse(
            query=payload.query,
            total_results=1,
            results=[
                SearchResult(
                    rank=1,
                    score=0.91,
                    filename="paper.pdf",
                    page_number=3,
                    excerpt="semantic search result excerpt",
                )
            ],
        )


@pytest.fixture
def client_with_stub_service(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, StubSearchService]:
    service = StubSearchService()
    settings = Settings(
        data_dir=tmp_path / "data",
        raw_data_dir=tmp_path / "data" / "raw",
        processed_data_dir=tmp_path / "data" / "processed",
        index_dir=tmp_path / "data" / "indices",
    )
    settings.ensure_directories()

    app.dependency_overrides[get_search_service] = lambda: service
    monkeypatch.setattr(upload_routes, "get_settings", lambda: settings)

    with TestClient(app) as client:
        yield client, service

    app.dependency_overrides.clear()


def test_upload_pdf_returns_document_summary(
    client_with_stub_service: tuple[TestClient, StubSearchService],
) -> None:
    client, service = client_with_stub_service

    response = client.post(
        "/upload",
        files={"file": ("paper.pdf", BytesIO(b"%PDF-1.4\n%stub"), "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json() == {
        "document_id": "doc-123",
        "filename": "paper.pdf",
        "page_count": 2,
        "chunk_count": 4,
    }
    assert service.original_filenames == ["paper.pdf"]
    assert service.ingested_paths[0].name.endswith("_paper.pdf")


def test_upload_rejects_non_pdf_files(
    client_with_stub_service: tuple[TestClient, StubSearchService],
) -> None:
    client, service = client_with_stub_service

    response = client.post(
        "/upload",
        files={"file": ("notes.txt", BytesIO(b"plain text"), "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."
    assert service.ingested_paths == []


def test_search_route_returns_ranked_results(
    client_with_stub_service: tuple[TestClient, StubSearchService],
) -> None:
    client, _ = client_with_stub_service

    response = client.post("/search", json={"query": "semantic retrieval", "top_k": 1})

    assert response.status_code == 200
    assert response.json() == {
        "query": "semantic retrieval",
        "total_results": 1,
        "results": [
            {
                "rank": 1,
                "score": 0.91,
                "filename": "paper.pdf",
                "page_number": 3,
                "excerpt": "semantic search result excerpt",
            }
        ],
    }