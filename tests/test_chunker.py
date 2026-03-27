from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_loader import ExtractedPage


def test_chunk_pages_creates_overlapping_windows() -> None:
    pages = [ExtractedPage(page_number=1, text="one two three four five six")]

    chunks = chunk_pages(
        pages,
        document_id="doc-1",
        filename="sample.pdf",
        chunk_size=4,
        chunk_overlap=2,
    )

    assert [chunk.text for chunk in chunks] == [
        "one two three four",
        "three four five six",
    ]